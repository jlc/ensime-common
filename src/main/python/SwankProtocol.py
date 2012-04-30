# SwankProtocol.py
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

  @SwankMethod("swank:format-source")
  def formatSource(filenames): pass

  #@SwankMethod("swank:public-symbol-search")

  #@SwankMethod("swank:import-suggestions")

  @SwankMethod("swank:completions")
  def completions(filename, offset, limit, case): pass

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

