# TestHelper.py
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

import sys
sys.path.append("../../main/python")
from Helper import *

log = logging.getLogger('TestHelper')

def testFindLastDist():
  listFiles = [
    '/Users/jeanluc/Sources/oh', '.dear', 'world',
    '/Users/jeanluc/Sources/ensime/dist_2.8.1',
    'dist_1.0.0', 'dist_2.1.12-RC2'
  ]

  good = 'dist_2.9.2-RC2'
  listFiles.append(good)
  last = findLastDist(listFiles)
  if last != good:
    print("testFindLastDist: failed - "+last)
    return False

  return True


testThemAll = [
  testFindLastDist
]

def main():
  for testFct in testThemAll:
    if not testFct():
      print("Test function failed")
      return 1

  print("All tests passed")
  return 0

if __name__ == '__main__':
  ret = main()
  sys.exit(ret)

