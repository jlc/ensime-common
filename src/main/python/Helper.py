# Helper.py
#
# Copyright (c) 2012, Jeanluc Chasseriau <jeanluc@lo.cx>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of ENSIME nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Aemon Cannon BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import types
import sys
import traceback
import re

#
# Simple Singleton decorator
#
# Be carefull: does not call parents initialization
def SimpleSingleton(cls):
  instances = {}
  def instance():
    if cls not in instances:
      instances[cls] = cls()
    return instances[cls]
  return instance

# list given object attributes, and call fct(attrname, obj.attr) for each of them
# return the list of attributes as string
def listObjectAttribute(obj, fct):
    s = []
    for it in dir(obj):
      if it[:2] == "__": continue
      attr = getattr(obj, it)
      if type(attr) == types.MethodType: continue
      fct(it, attr)
      s.append(it)
    return s

@SimpleSingleton
class Logger:
  DEBUG = 0
  INFO = 1
  WARN = 2
  ERROR = 3
  CRITICAL = 4
  LOG_TY_STR = {
    DEBUG: 'DEBUG', INFO: 'INFO', WARN: 'WARN', 
    ERROR: 'ERROR', CRITICAL: 'CRITICAL'
  }
  TO_FILE = 0
  TO_STDOUT = 1
  def __init__(self):
    self.file = None
    self.filename = ""
    self.outputs = {self.TO_FILE: None, self.TO_STDOUT: None}
    self.minLogLevel = self.DEBUG
  def setOutput(self, filename):
    try: self.file = file(filename, 'a', 1)
    except:
      print("Logger.setOutput: unable to open file ("+filename+")")
      self.outputs[self.TO_FILE] = None
      return False
    self.filename = filename
    self.outputs[self.TO_FILE] = self.logToFile
    return True
  def useStdOut(self, b):
    if b:
      self.outputs[self.TO_STDOUT] = self.logToStdOut
    else:
      self.outputs[self.TO_STDOUT] = None
  def setMinLogLevel(self, lvl):
    if lvl < 0 or lvl > self.CRITICAL:
      print("Logger.setMinLogLevel: cannot set such a log level ("+str(lvl)+")")
      return False
    self.minLogLevel = lvl
    return True
  def logToFile(self, s):
    try:
      self.file.write(s)
      self.file.flush()
    except:
      print("Logger.logToFile: unable to write in file")
  def logToStdOut(self, s):
    try:
      sys.stdout.write(s)
      sys.stdout.flush()
    except:
      print("Logger.logToStdOut: unable to log to stdout")
  def log(self, ty, s):
    if ty < self.minLogLevel: return
    l = self.LOG_TY_STR[ty] + ' : ' + s + "\n"
    for fct in self.outputs.values():
      if fct != None: fct(l)
  def debug(self, s): self.log(self.DEBUG, s)
  def info(self, s): self.log(self.INFO, s)
  def warn(self, s): self.log(self.WARN, s)
  def error(self, s): self.log(self.ERROR, s)
  def critical(self, s): 
    self.log(self.CRITICAL, s)
    sys.exit(1)

#
# Catch And Log Exception decorator
#
def CatchAndLogException(mth):

  def methodWrapper(*args, **kwargs):

    msg = "[ Exception catched and logged by @CatchAndLogException ]"

    def toDefaultLog():
      try:
        filelog = open("python_exceptions.log","a")
        filelog.write(msg+"\n")
        traceback.print_exc(file=filelog)
      except: pass

    def toLogger():
      Logger().error(msg)
      traceback.print_exc(file=Logger().file)

    def toSysErr():
      sys.stderr.write(msg+"\n")
      traceback.print_exc(file=sys.stderr)

    # TODO: vim on MacOSX does not appreciate
    # maybe we can buffer it somewhere and then print with feedkeys()
    #outputs = [toSysErr]
    outputs = []

    if Logger().file == None:
      outputs.append(toDefaultLog)
    else:
      outputs.append(toLogger)

    try: mth(*args, **kwargs)
    except:
      for out in outputs:
        out()

  return methodWrapper

# findLastDist(filesList)
# return the name of the last distribution (last version number)
def findLastDist(filesList):
  regexp = re.compile("^.*dist_(\d+\.\d+\.\d+).*")
  dists = []

  for file in filesList:
    match = regexp.match(file)
    if match == None: continue
    grps = match.groups()

    if len(grps) > 0:
      dists.append( {'filename':file, 'version':grps[0]} )

  if not len(dists):
    return None

  def compare(a, b):
    va = a['version'].split('.')
    vb = b['version'].split('.')
    i = 0

    while i < len(va):
      if i+1 > len(vb): return 1
      if va[i] == vb[i]: i += 1
      elif va[i] < vb[i]: return -1
      else: return 1

    return 0

  dists.sort(cmp = compare)
  return dists.pop()['filename']
