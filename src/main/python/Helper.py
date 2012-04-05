# Helper.py
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
