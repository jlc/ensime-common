# SwankProtocol.py
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

# SwankCaller usage:
# To call a method:
#   class Handler(SwankCallHandler):
#     def response(self, response):
#       # response is a python object
#       pass
#
#   SwankRpc().connectionInfo(args)(Handler())
#
# SwankEvent usage:
# To receive an event:
#   @SwankIndexerReady
#   class MyEvent(SwankEvent):
#     def event(self, args):
#       # args is a python object
#       pass
#
# That's it!

from SwankProtocolHelper import *
from Helper import SimpleSingleton

# Swank Rpc Caller

@SimpleSingleton
@SwankCaller("swank-rpc")
class SwankRpc:

  @SwankMethod("swank:connection-info")
  def connectionInfo(): pass

  @SwankMethod("swank:init-project")
  def projectInit(projectPropertiesList): pass

  @SwankMethod("swank:typecheck-file")
  def typecheckFile(filename): pass

  @SwankMethod("swank:typecheck-all")
  def typecheckAll(): pass

  @SwankMethod("swank:uses-of-symbol-at-point")
  def usesOfSymbolAtPoint(filename, offset): pass

  #@SwankMethod("swank:type-by-id")
  #def typeById(typeId)

  #@SwankMethod("swank:type-by-name")
  #def typeByName(typeName)

  #@SwankMethod("swank:type-by-name-at-point")
  #def typeByNameAtPoint(typeName, filename, offset)

  #@SwankMethod("swank:type-at-point")
  #def typeAtPoint(filename, offset): pass

  #@SwankMethod("swank:inspect-type-at-point")
  #def inspectTypeAtPoint(filename, offset): pass

  #@SwankMethod("swank:inspect-type-by-id")
  #def inspectTypeById(typeId): pass

  @SwankMethod("swank:symbol-at-point")
  def symbolAtPoint(filename, offset): pass

  #@SwankMethod("swank:inspect-package-by-path")
  #def inspectPackageByPath(qualifiedPackageName): pass

  #@SwankMethod("swank:prepare-refactor")
  #def prepareRefactor(id, mannerSymbol, ...): pass

  #@SwankMethod("swank:exec-refactor")
  #def execRefactor(id, mannerSymbol)
  # manner: Symbol: rename, extractMethod, extractLocal, organizeImports, or addImport

  #@SwankMethod("swank:cancel-refactor")
  #def cancelRefactor(id): pass

  #@SwankMethod("swank:symbol-designations")
  #def symbolDesignations(filename, startOffset, endOffset, symbolsList)
  # symbolsList: var,val,varField,valField,functionCall, operator,param,class,trait,object

  #@SwankMethod("swank:expand-selection")
  #def expandSelection(filename, startOffset, endOffset): pass

  @SwankMethod("swank:shutdown-server")
  def shutdownServer(): pass


# Swank events

@SwankDefineEvent("background-message")
class SwankEventBackgroundMessage: pass

@SwankDefineEvent("reader-error")
class SwankEventReaderError: pass

@SwankDefineEvent("compiler-ready")
class SwankEventCompilerReady: pass

@SwankDefineEvent("full-typecheck-finished")
class SwankEventFullTypecheckFinished: pass

@SwankDefineEvent("indexer-ready")
class SwankEventIndexerReady: pass

@SwankDefineEvent("scala-notes")
class SwankEventScalaNotes: pass

@SwankDefineEvent("java-notes")
class SwankEventJavaNotes: pass

@SwankDefineEvent("clear-all-scala-notes")
class SwankEventClearAllScalaNotes: pass

@SwankDefineEvent("clear-all-java-notes")
class SwankEventClearAllJavaNotes: pass

class ProtocolConst(object):
  MsgCompilerUnexpectedError        = 101
  MsgInitializingAnalyzer           = 102

  MsgBuildingEntireProject          = 103
  MsgBuildComplete                  = 104
  MsgMisc                           = 105

  ErrExceptionInRPC                 = 201
  ErrMalformedRPC                   = 202
  ErrUnrecognizedForm               = 203
  ErrUnrecognizedRPC                = 204
  ErrExceptionInBuilder             = 205

  ErrPeekUndoFailed                 = 206
  ErrExecUndoFailed                 = 207

  ErrFormatFailed                   = 208

  ErrAnalyzerNotReady               = 209
  ErrExceptionInAnalyzer            = 210

  ErrFileDoesNotExist               = 211

  ErrExceptionInIndexer             = 212

  constDict = {
    MsgCompilerUnexpectedError:     "MsgCompilerUnexpectedError",
    MsgInitializingAnalyzer:        "MsgInitializingAnalyzer",
    MsgMisc:                        "MsgMisc",

    MsgBuildingEntireProject:       "MsgBuildingEntireProject",
    MsgBuildComplete:               "MsgBuildComplete",

    ErrExceptionInRPC:              "ErrExceptionInRPC",
    ErrMalformedRPC:                "ErrMalformedRPC",
    ErrUnrecognizedForm:            "ErrUnrecognizedForm",
    ErrUnrecognizedRPC:             "ErrUnrecognizedRPC",
    ErrExceptionInBuilder:          "ErrExceptionInBuilder",

    ErrPeekUndoFailed:              "ErrPeekUndoFailed",
    ErrExecUndoFailed:              "ErrExecUndoFailed",

    ErrFormatFailed:                "ErrFormatFailed",

    ErrAnalyzerNotReady:            "ErrAnalyzerNotReady",
    ErrExceptionInAnalyzer:         "ErrExceptionInAnalyzer",

    ErrFileDoesNotExist:            "ErrFileDoesNotExist",

    ErrExceptionInIndexer:          "ErrExceptionInIndexer"
  }

  @staticmethod
  def toStr(no): return ProtocolConst.constDict[no]

