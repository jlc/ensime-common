# SExpression.py
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

# TODO:
# - clarify the use of toValue() / toWire() / toPy()

import re
import types
import logging

from Helper import *

log = logging.getLogger('ensime-common')

# S-Expression Python Object representation
# Base object of S-Expression to python conversion
class SExpPyObject(object):
  def debugString(self):
    s = []

    def helper(attrname, selfattr):
      if isinstance(selfattr, SExpPyObject):
        s.append("%s: %s" % (attrname, selfattr.debugString()))
      # TODO: not sure if we handle the case properly here (test with scala-notes sexp)
      if isinstance(selfattr, types.ListType):
        i = 0
        s.append('%s: [' % (attrname))
        for item in selfattr:
          helper(str(i), item)
          i += 1
        s.append(']')
      else:
        s.append("%s: %s" % (attrname, str(selfattr)))

    listObjectAttribute(self, helper)
    return str(self) +": {" + ' '.join(s) + "}"

  def has(self, attrname):
    return hasattr(self, attrname)

# S-Expression
class SExp(object):
  def __init__(self): pass
  def __str__(self): return "SExp"
  def toWire(self): return "SExp"
  def toValue(self): return None
  def debugString(self): return "SExp"

# S-Expression List
class SExpList(SExp):
  def __init__(self, items = []):
    self.items = items
  def __str__(self): return "SExpList"
  def toWire(self): return '(' + ' '.join(sexp.toWire() for sexp in self.items) + ')'
  def debugString(self):
    s = "SExpList: "+'(' + "\n"
    s += "\n".join(sexp.debugString() for sexp in self.items) + ')'
    return s
  def toItems(self): return self.items
  def toValue(self): return self._toPyList()
  def _toPyList(self):
    li = []
    for it in self.items:
      if isinstance(it, SExpList) and it.hasKeyword():
        li.append(it.toPy())
      else:
        li.append(it.toValue())
    return li
  def _toPyObject(self):
    attrs = {}
    it = self.items.__iter__()

    while True:
      try: v = it.next()
      except: break

      if isinstance(v, KeywordAtom):
        value = it.next()
        if isinstance(value, SExpList):
          value = value.toPy()
        else:
          value = value.toValue()
        attrs[v.asName().replace('-','_')] = value
      else:
        # TODO: Not sure if it's printed in case (:return :ok () 42) -> what happen to 42??
        log.error("SExpList.toPy: cannot convert to object: '"+str(v)+"' is not a KeywordAtom")
   
    Ty = type('SExpPyObj', (SExpPyObject,), attrs)
    return Ty()
  def hasKeyword(self):
    for it in self.items:
      if isinstance(it, KeywordAtom):
        return True
    return False
  def toPy(self):
    if self.hasKeyword():
      return self._toPyObject()
    else:
      return self._toPyList()

class BooleanAtom(SExp):
  def __init__(self): pass
  def toBool(self): pass

class NilAtom(BooleanAtom):
  def __init__(self): pass
  def __str__(self): return 'NilAtom'
  def toWire(self): return 'nil'
  def debugString(self): return "NilAtom: " + 'nil'
  def toBool(self): return False 
  def toPy(self): return self.toBool()
  def toValue(self): return self.toBool()

class TruthAtom(BooleanAtom):
  def __init__(self): pass
  def __str__(self): return 'TruthAtom'
  def toWire(self): return 't'
  def debugString(self): return "TruthAtom: " + 't'
  def toBool(self): return True
  def toPy(self): return self.toBool()
  def toValue(self): return self.toBool()

class StringAtom(SExp):
  def __init__(self, value):
    if value[0] == '"' or value[0] == "'": value = value[1:]
    if value[-1] == '"' or value[-1] == "'": value = value[:-1]
    self.value = value
  def __str__(self): return 'StringAtom'
  def toWire(self): return '"'+self.value+'"'
  def toValue(self): return self.value
  def debugString(self): return "StringAtom: " + self.value

class IntAtom(SExp):
  def __init__(self, value): self.value = value
  def __str__(self): return 'IntAtom'
  def toWire(self): return str(self.value)
  def toValue(self): return self.value
  def debugString(self): return "IntAtom: " + str(self.value)

class SymbolAtom(SExp):
  def __init__(self, value):
    self.value = value
  def __str__(self): return 'SymbolAtom'
  def toWire(self): return self.value
  def toValue(self): return self.value
  def debugString(self): return 'SymbolAtom: ' + self.value

class KeywordAtom(SExp):
  def __init__(self, value):
    if value[0] != ':': value = ':'+value
    self.value = value
  def __str__(self): return 'KeywordAtom'
  def toWire(self): return self.value
  def toValue(self): return self.value
  def debugString(self): return "KeywordAtom: " + self.value
  def asName(self):
    # strip '^:'
    return self.value[1:]

# Tools:

@SimpleSingleton
class SExpConverter:
  def __init__(self):
    self.reList = re.compile('^\(.*\)$')
    self.reInt = re.compile('^-?\d+$')
    self.reKeyword = re.compile('^:[\w\-]+$')
    self.reString = re.compile('^[\'"]{1}.*[\'"]{1}$')

  def wireToSExp(self, s):
    s = s.strip()

    if s == 'nil':
      return NilAtom()
    elif s == 't':
      return TruthAtom()
    elif self.reInt.match(s):
      return IntAtom(int(s))
    elif self.reKeyword.match(s):
      return KeywordAtom(s)
    elif self.reString.match(s):
      return StringAtom(s)
    else:
      return StringAtom(s)

  def pyToSExp(self, py):

    if isinstance(py, types.BooleanType):
      # BooleanType are IntType too!
      if py: return TruthAtom()
      else: return NilAtom()
    elif isinstance(py, types.IntType):
      return IntAtom(py)
    elif isinstance(py, types.StringType):
      py = py.strip()
      if py[0] == ':':
        return KeywordAtom(py)
      elif py == 'nil':
        return NilAtom()
      elif py == 't':
        return TruthAtom()
      elif py.startswith('swank:'):
        return SymbolAtom(py)
      else:
        return StringAtom(py)
    elif isinstance(py, types.ListType):
      items = []
      for i in py:
        sexp = self.pyToSExp(i)
        if sexp != None:
          items.append(sexp)
      return SExpList(items)
    elif isinstance(py, types.DictType):
      items = []
      for key in py.keys():
        key = key.replace('_', '-')
        items.append(KeywordAtom(key))
        items.append(self.pyToSExp(py[key]))
      return SExpList(items)
    elif isinstance(py, SExpPyObject):
      items = []
      def helper(attrname, pyattr):
        attrname = attrname.replace('_', '-')
        sexp = self.pyToSExp(pyattr)
        if sexp != None:
          items.append(KeywordAtom(attrname))
          items.append(sexp)

      listObjectAttribute(py, helper)
      return SExpList(items)
    elif isinstance(py, types.MethodType):
      log.warn("pyToSExp: Method cannot be converted to SExp")
      return None
    else:
      log.error("pyToSExp: argument ("+str(py)+") cannot be converted to SExp")
      return None

  def toWire(self, se):
    if isinstance(se, SExp):
      return se.toWire()
    else:
      log.error("SExpConverter: given object is not a SExp")
      return None

# Quick SExpression Parser specificaly adapted to ensime
# A time will come when it will be re-implemented nicely
# improving robustess and efficiency
# TODO: make that time happen
class SExpParser:
  def __init__(self):
    pass

  def parse(self, s):

    def matchingBracketPos(s):
      inDoubleQuote = False
      inQuote = False
      found = False
      cpt = 0
      i = 0
      max = len(s)

      while not found and i < max:
        if s[i] == '"':
          inDoubleQuote = not inDoubleQuote
        elif s[i] == "'":
          inQuote = not inQuote
        elif s[i] == "\\":
          i += 1 # escape next char
        elif not inDoubleQuote and not inQuote and s[i] == '(':
          cpt += 1
        elif not inDoubleQuote and not inQuote and s[i] == ')':
          cpt -= 1
          if cpt == 0: 
            found = True
            break
        i += 1
  
      if found:
        return i
      return None

    def subParse(s):
      s = s.strip()

      items = []
      i = 0
      max = len(s)
      flag = True

      beginToken = -1

      while i < max:
        
        if s[i] == '(':
          end = matchingBracketPos(s[i:])
          if end == None:
            log.error("subParse: cannot find matching bracket! abording!")
            return SExpList([])
          else:
            end += i
            items.append(subParse(s[i+1:end]))
            i = end + 1
      
        elif s[i] == '"':
          # TODO: What about \" here?
          end = s.find('"', i+1)
          if end == -1:
            log.error("subParse: cannot find matching double-quote! abording!")
            return SExpList([])
          else:
            end += 1
            items.append(SExpConverter().wireToSExp(s[i:end]))
            i = end + 1

        elif s[i] == ' ' or s[i] == "\n" or s[i] == "\t":
          if beginToken != -1:
            items.append(SExpConverter().wireToSExp(s[beginToken:i]))
            beginToken = -1
          i += 1

        else:
          if beginToken == -1:
            beginToken = i
          i += 1

      if beginToken != -1:
        items.append(SExpConverter().wireToSExp(s[beginToken:i]))

      #if len(items) == 0:
      #  print("error: subParse: no items!")
      
      return SExpList(items)

    return subParse(s).items[0]


