#!/usr/bin/env python

# EnsimeClient.py
#
# Copyright 2012 Jeanluc Chasseriau <jeanluc@lo.cx>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import socket
import select
import time
import logging
from optparse import OptionParser

log = logging.getLogger('EnsimeClient')

# try to find directories 'lib/common' or 'src/main/python' to import dependencies
def sourceFinder(directory):
  try: entries = os.listdir(directory)
  except: return None

  entries.sort(key=str.lower)
  entries.reverse()

  for entry in entries:
    if entry == 'src':
      return directory + '/src/main/python'

  parts = directory.split('/')
  directory = '/'.join(parts[:-1])

  return sourceFinder(directory)

directory = sourceFinder(os.path.dirname(sys.argv[0]))
if directory == None:
  print("Unable to find common python directory")
  sys.exit(1)

sys.path.append(directory)

try:
  from Helper import *
except:
  print("Unable to find Helper.py")
  sys.exit(1)

DEFAULT_LOG_FILENAME = 'EnsimeClient.log'

class Proxy:
  """Base class providing basic proxy features: read and write"""

  class Read:
    def __init__(self, serverSocket):
      self.serverSocket = serverSocket
      self.buf = bytearray(4096)

    def server(self):

      def readUntil(size):
        data = ''
        while size > 0:
          s = 4096
          if size <= s: s = size

          s = self.serverSocket.recv_into(self.buf, s)
          decoded = self.buf[:s].decode("utf-8")
          data += decoded
          size -= len(decoded)
        return data

      # note: the size given in Swank header correspond to the length of the string which follow,
      # which may differ from the real number of bytes (depending on encoding. e.g. utf-8)
      # take care to a) decode() b) calculate using len(decoded)
      try:
        hexSize = self.serverSocket.recv(6)
        size = int(hexSize, 16)
        data = readUntil(size)
      except Exception as e:
        log.exception("Proxy.Read.server: unable to read data from server: " + str(e))
        return (None, None, None)
      return (size, hexSize, data)

    def stdin(self):
      try:
        data = sys.stdin.readline()
      except Exception as e:
        log.error("Proxy.Read.stdin: unable to read data from stdin: " + str(e))
        return None
      return data

  class Write:
    def __init__(self, serverSocket):
      self.serverSocket = serverSocket

    def server(self, data):
      try:
        self.serverSocket.sendall(data)
      except Exception as e:
        log.error("Proxy.Write.server: unable to send data to server: " + str(e))
        return False
      return True

    def stdout(self, data):
      try:
        sys.stdout.write(data)
        sys.stdout.flush()
      except Exception as e:
        log.error("Proxy.Write.stdout: unable to write data to stdout: " + str(e))
        return False
      return True

  def __init__(self, serverSocket):
    self.serverSocket = serverSocket
    self.read = self.Read(serverSocket)
    self.write = self.Write(serverSocket)

class RawProxy(Proxy):
  """Raw Proxy: without add or changes on data"""

  def __init__(self, serverSocket):
    Proxy.__init__(self, serverSocket)

  def fromServer(self):
    (size, hexSize, data) = self.read.server()
    if size == None:
      return False

    log.debug("server: " + hexSize + data)

    if not self.write.stdout(hexSize + data + "\n"):
      return False

    return True

  def fromStdin(self):
    data = self.read.stdin()
    if data == None:
      return False

    log.debug("stdin: " + data.strip())

    if not self.write.server(data):
      return False

    return True

class SwankProxy(Proxy):
  """Swank Proxy: provide abstraction of the swank protocol"""

  def __init__(self, serverSocket):
    Proxy.__init__(self, serverSocket)

  def fromServer(self):
    (size, hexSize, data) = self.read.server()
    if size == None:
      return False

    log.debug("server: " + hexSize + data)

    if not self.write.stdout(data + "\n"):
      return False

    return True

  def fromStdin(self):
    data = self.read.stdin()
    if data == None:
      return False

    log.debug("stdin: " + data.strip())

    dataSize = "%06x" % (len(data))
    if not self.write.server(dataSize + data):
      return False

    return True

def usage():
  helplist = [
    '[-l|--log logfilename]',
    '[-f|--portfile port_filename]',
    '[-p|--port port_number]',
    '[-r|--raw]'
  ]

  print("Usage: %s %s" % (sys.argv[0], ' '.join(helplist)))
  print("")
  sys.exit(1)

@CatchAndLogException
def main():

  parser = OptionParser()
  parser.add_option('-l', '--log',
                    dest='log',
                    help='log filename')
  parser.add_option('-f', '--portfile',
                    dest='portfile',
                    help='port file to read tcp port from')
  parser.add_option('-p', '--port',
                    dest='port',
                    help='tcp port number')
  parser.add_option('-r', '--raw',
                    dest='raw',
                    action="store_true",
                    help='raw mode')

  (options, args) = parser.parse_args()

  logfile = DEFAULT_LOG_FILENAME
  if options.log != None:
    logfile = options.log

  initLog('', logfile)

  if options.port != None:
    try: port = int(options.port)
    except:
      log.error("Invalid given port number ("+options.port+")")
      return 1

  elif options.portfile != None:
    try:
      f = file(options.portfile)
      port = f.readline()
      f.close()
      port = int(port)
    except:
      log.error("Unable to read port from: "+options.portfile)
      return 1

  else:
    usage()
    return 1

  
  addr = ("localhost", port)
  try:
    serverSocket = socket.create_connection(addr)
  except:
    log.error("Unable to connect to swank server "+str(addr))
    return 1

  proxy = None
  if options.raw:
    proxy = RawProxy(serverSocket)
  else:
    proxy = SwankProxy(serverSocket)

  runProxy(proxy)

  serverSocket.close()

  log.info("done")

  return 0

def runProxy(proxy):

  def serverError():
    log.error("runProxy: serverError: server error")
    return False

  def stdinError():
    log.error("runProxy: stdinError: stdin error")
    return False

  flag = True
  input = [proxy.serverSocket, sys.stdin]
  output = []
  error = [proxy.serverSocket, sys.stdin]
  timeout = 0.1 # sec

  inputHandlers = {proxy.serverSocket: proxy.fromServer, sys.stdin: proxy.fromStdin}
  errorHandlers = {proxy.serverSocket: serverError, sys.stdin: stdinError}

  while flag:
    try:
      (i, o, e) = select.select(input, output, error, timeout)
    except BaseException as e:
      log.error("Handling exception: " + str(e))
      flag = False

    for ii in i:
      if not inputHandlers[ii]():
        flag = False

    for ee in e:
      if not errorHandlers[ee]():
        flag = False

if __name__ == "__main__":
  r = main()
  sys.exit(r)


