# SwankProtocolHelper.py
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

from Helper import SimpleSingleton, Logger
from SExpression import *

# Response handler class
class SwankCallHandler(object):
  def __init__(self): pass
  def response(self, response): pass
  def abort(self, code, details): pass

# Represent a Call
class SwankCall(object):
  # the ultimate answer to Life, the Universe and Everything
  __nextCallId__ = 42

  @staticmethod
  def nextCallId():
    n = SwankCall.__nextCallId__
    SwankCall.__nextCallId__ += 1
    return n

  def __init__(self):
    self.caller = "" # e.g. swank-rpc
    self.method = "" # e.g. swank:connection-info
    self.args = None # swank-rpc arguments as list of python object
    self.handler = None # SwankCallHandler
    self.callId = SwankCall.nextCallId()

  def setCaller(self, caller):
    self.caller = caller

  def setMethod(self, mthName):
    self.method = mthName

  def setArgs(self, args):
    self.args = args

  def setHandler(self, handler):
    self.handler = handler

  def asSExp(self):
    items = []
    items.append(self.caller)
    subItems = []
    subItems.append(self.method)
    subItems.extend(self.args)
    items.append(subItems)
    items.append(self.callId)
    return SExpConverter().pyToSExp(items)

  def send(self):
    SwankProcessor().send(self)

# Represent an event
class SwankEvent(object):
  def event(self, *args): pass

# Decorator: define a SwankCaller (e.g. swank-rpc)
def SwankCaller(name):

  def nest(cls):

    cls.__SwankCaller__ = name
    return cls

  return nest

# Decorator: define a SwankMethod within a SwankCaller
def SwankMethod(name):

  def nest(mth):

    # args are python objects (not SExp)
    def newMethod(self, *args):

      def handlerMethod(handler):
        call = SwankCall()
        call.setCaller(':'+self.__SwankCaller__)
        call.setMethod(name)
        call.setArgs(args)
        call.setHandler(handler)
        call.send()
        return None

      return handlerMethod

    return newMethod

  return nest

# Decorator: define a SwankEvent by transforming the class in decorator
# @todo: add SwankEvent as parent class automatically
def SwankDefineEvent(name):

  def nest(cls):

    def __init__(self, mth):
      SwankProcessor().registerEvent(KeywordAtom(name), mth)

    cls.__init__ = __init__
    return cls

  return nest


@SimpleSingleton
class SwankProcessor(object):

  def __init__(self):
    self.parser = SExpParser()
    self.callHandler = {}     # callId: SwankCall
    self.eventHandler = {}    # eventName: method
    self.sendFct = None       # function to execute 'send'
    self.messages = self.BufferMessage()    # handle messages buffering

  def setSendFunction(self, fct):
    self.sendFct = fct

  def registerEvent(self, keywordAtom, handler):
    kwValue = keywordAtom.toValue()

    if self.eventHandler.has_key(kwValue):
      Logger().warn("Processor.registerEvent: event '"+kwValue+"' is already registered")

    Logger().debug("Processor.registerEvent: registering event: " + kwValue)
    self.eventHandler[kwValue] = handler

  def processReturn(self, sexpArgs, callId):
    Logger().debug("Processor.processReturn: handling 'return': callId: "+str(callId))

    if not isinstance(sexpArgs, SExpList):
      Logger().error("Processor.processReturn: response argument is not a list")
      Logger().error("Processor.processReturn: " + sexpArgs.debugString())
      return

    if not self.callHandler.has_key(callId):
      Logger().error("Processor.processReturn: callId ("+str(callId)+") not registered")
      return

    items = sexpArgs.toItems()

    if items[0].toValue() == ":ok":
      args = items[1].toPy()

      self.callHandler[callId].handler.response(args)
      del(self.callHandler[callId])

    elif items[0].toValue() == ":abort":
      code = items[1].toValue()
      details = items[2].toValue()

      self.callHandler[callId].handler.abort(code, details)
      del(self.callHandler[callId])

    else:
      Logger().error("Processor.processReturn: unknown return value: "+items[0].toValue())

  def processEvent(self, eventName, sexpItems):
    if not self.eventHandler.has_key(eventName):
      Logger().debug("Processor.processEvent: unregistered event: "+eventName)
      return

    Logger().debug("Processor.processEvent: handling event: " + eventName)

    pyItems = []
    for item in sexpItems:
      if isinstance(item, SExpList):
        pyItems.append(item.toPy())
      else:
        pyItems.append(item.toValue())

    Logger().debug("Processor.processEvent: pyArgs: " + str(pyItems))

    self.eventHandler[eventName](*pyItems)

  @CatchAndLogException
  def process(self, data):

    self.messages.add(data)

    while self.messages.has():

      s = self.messages.get()

      sexplist = self.parser.parse(s)
      items = sexplist.toItems()

      if isinstance(items[0], KeywordAtom):

        # call response handling
        if items[0].toValue() == ":return":
          callId = items[2].toValue()

          self.processReturn(items[1], callId)

        # event handling
        else:
          eventName = items[0].toValue()

          self.processEvent(eventName, items[1:])

      else:
        Logger().error("Processor.process: unregognize first SExpression item: "+items[0].toValue())
        Logger().error("Processor.process: SExp:"+sexplist.debugString())


  # send(swankCall)
  @CatchAndLogException
  def send(self, call):
    
    if self.callHandler.has_key(call.callId):
      Logger().error("Processor.send: callId ("+str(call.callId)+") already registered")
      return False

    self.callHandler[call.callId] = call

    sexp = call.asSExp()

    Logger().debug("Processor.send: call (id:"+str(call.callId)+")")
    Logger().debug("Processor.send: sexp: "+sexp.toWire())
   
    if self.sendFct == None:
      Logger().error("Processor.send: send function has not been set")
      return

    data = sexp.toWire() + "\n"
    size = "%06x" % (len(data))

    self.sendFct(size + data)

  class BufferMessage:
    def __init__(self):
      self.messages = []
      self.rest = ''
      self.expectedSize = 0

    def add(self, data):

      def consume(data, size):
        return data[size:]

      data = self.rest + data
      self.rest = ''
      expect = self.expectedSize

      keepGoing = True
      while keepGoing:

        if expect == 0:
          try:
            expect = int(data[:6], 16)
            data = consume(data, 6)
          except:
            Logger().error("Buffer.add: expected header in hex but got: " + data)
            return False

        dataSize = len(data)

        if dataSize == expect:
          self.messages.append(data)
          expect = 0
          keepGoing = False

        elif dataSize < expect:
          self.rest = data
          keepGoing = False

        elif dataSize > expect:
          self.messages.append(data[:expect])
          data = consume(data, expect)
          expect = 0

      self.expectedSize = expect

    def has(self):
      if len(self.messages) > 0:
        return True
      return False

    def get(self):
      if len(self.messages) == 0:
        return None
      self.messages.reverse()
      e = self.messages.pop()
      self.messages.reverse()
      return e


