# xnote.py  (c)2019  Henrique Moreira (part of 'cotagente')

"""
  Process html from xperteleven...etc.

  Compatibility: python 2 and 3.
"""

from base64 import b64decode, b64encode


#
# test_xnote()
#
def test_xnote (aOutFile, errFile, inFile, inArgs):
  code = None
  isStdin = True
  myEncoding="ISO-8859-1"
  style = "text-flow"
  try:
    cmd = inArgs[ 0 ]
  except:
    return None
  param = inArgs[ 1: ]
  outFile = aOutFile
  if cmd=="de-base64":
    if len( param )<=0:
      fIn = inFile
    else:
      isStdin = False
      fIn = open( param[ 0 ], "r", encoding=myEncoding )
    if fIn:
      cont = fIn.read()
      lines = cont.split( "\n" )
      code = de_base64( lines, style, outFile, errFile )
  return code


#
# new_flush()
#
def new_flush (buf):
  if buf=="":
    return "", ""
  try:
    b = b64decode( buf ).decode( "ascii" )
  except:
    b = None
  if b is None:
    return "", buf
  return "", b


#
# non_base64()
#
def non_base64 (s):
  idx = 0
  for a in s:
    isOk = a.isalpha() or a.isdigit() or a in ( "+", "/", "=" )
    if not isOk:
      return idx
    idx += 1
  return -1


#
# is_base64()
#
def is_base64 (s):
  return s!="" and non_base64( s )==-1


#
# de_base64()
#
def de_base64 (lines, style, outFile, errFile):
  assert type( style )==str
  isNormal = style=="text-flow"
  idx = 0
  pre = ""
  buf = ""
  remember = False
  for line in lines:
    idx += 1
    sLine = line.strip()
    if sLine=="":
      if remember:
        outFile.write("\n")
        remember = False
      buf, s = new_flush( buf )
    else:
      remember = (buf=="" or is_base64( buf )) and is_base64( sLine )
      if remember:
        buf += sLine
        continue
      else:
        buf, s = new_flush( buf+sLine )
    #pre = "{}: ".format( idx )
    try:
      outFile.write("{}{}\n".format( pre, s ))
    except:
      errFile.write("Cannot write line: {}\n".format( idx ))
  buf, s = new_flush( buf )
  if s!="":
    outFile.write("{}\n".format( s ))
  return 0


#
# Test suite
#
if __name__ == "__main__":
  import sys
  from sys import stdin, stdout, stderr
  args = sys.argv[ 1: ]
  code = test_xnote( stdout, stderr, stdin, args )
  if code is None:
    code = 0
    print("""xnote.py command [options]

Commands are:
   de-base64
""")
  sys.exit( code )
