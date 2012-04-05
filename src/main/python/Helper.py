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
import logging

# NOTE: Remember to initialize a Logger for 'ensime-common'

# initialize a high level of logger called 'mainlogger'
# all sublogger should be prefixed by 'mainlogger'
def initLog(mainlogger, filename, stdout = False):
  log = logging.getLogger(mainlogger)

  FORMAT =    '%(asctime)s %(levelname)s [%(name)s] '
  FORMAT +=   '%(message)s'
  #FORMAT +=   '%(message)s (%(funcName)s(), %(filename)s:%(lineno)d)'

  formatter = logging.Formatter(fmt=FORMAT)

  handlers = []
  handlers.append(logging.FileHandler(filename))

  if stdout:
    handlers.append(logging.StreamHandler())

  for h in handlers:
    h.setFormatter(formatter)
    log.addHandler(h)

  log.setLevel(logging.DEBUG)
  log.propagate = False

def CatchAndLogException(mth):
  def methodWrapper(*args, **kwargs):
    log = logging.getLogger('ensime-common')
    try: mth(*args, **kwargs)
    except:
      log.exception("[ CatchAndLogException ]")

  return methodWrapper

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
