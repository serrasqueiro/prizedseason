# office_leaves.py  (c)2019  Henrique Moreira (part of 'horaconta')

"""
  office_leaves script works 'Office Leaves' sheets

  Compatibility: python 2 and 3.
"""

from sys import stdin, stdout, stderr
import xml.etree.ElementTree as ET
import os.path
import datetime
from bdate import *

errorInfo = stderr
#errorInfo = None  # uncomment this line to avoid too much verbose output


#
# main_run() -- main run
#
def main_run (outFile, errFile, inArgs):
  code = None
  verbose = 0
  xdbDir = "../xdb_etc"
  absXml = "off_abs.xml"
  try:
    cmd = inArgs[ 0 ]
  except:
    return None

  param = inArgs[ 1: ]

  while len( param )>0 and param[ 0 ].startswith( "-" ):
    if param[ 0 ].startswith( "-v" ):
      verbose += param[ 0 ].count( "v" )
      del param[ 0 ]
      continue
    if param[ 0 ]=="--xdb-dir":
      xdbDir = param[ 1 ]
      del param[ :2 ]
      continue

  ioXml = os.path.join( xdbDir, absXml )

  opts = {"verbose":verbose,
          "xdb-dir":xdbDir,
          }

  if cmd=="version":
    print("version", version)
    if verbose>0:
      misc_help( xdbDir, absXml )
    return 0

  if cmd=="dump":
    if len( param[ 0 ] )>0:
      ioXml = param[ 0 ]
    code = cmd_dump( outFile, ioXml, opts )
    return code

  if cmd=="read-raw":
    basicSample = """
	<OffList date1="@1@" date2="@2@" abstype="@3@"@4@>
	</OffList>
"""
    code = cmd_read_raw( outFile, ioXml, param, basicSample, opts )
    return code

  return code


#
# misc_help()
#
def misc_help (**args):
  print("args:", args)
  return 0


#
# cmd_dump()
#
def cmd_dump (outFile, ioXml, opts):
  def processor (root, debug=0):
    rTag = root.tag
    cont = []
    dVal = {"HO":0,
            }
    for line in root:
      absType = line.attrib[ "abstype" ]
      strDate1 = line.attrib[ "date1" ]
      if debug>0:
        print("LINE:", line.attrib)
        print("dVal['{}']={}".format( absType, dVal[ absType ]))
      try:
        strDate2 = line.attrib[ "date2" ]
      except:
        strDate2 = strDate1
      for hint in line:
        binCont = ET.tostring( hint )
        sComment = basic_ascii_tree( binCont )
        if debug>0:
          print("HINT: {}-{}".format( strDate1, strDate2 ), hint.tag.split("}")[-1], "tag={}, is: '{}'".format( hint.tag, sComment ))
      fr = BDate( strDate1 )
      to = BDate( strDate2 )
      days = to.diff( fr, 1 )
      assert days>0
      if to.asValue <= dVal[ absType ]:
        lastWas = BDate( str( dVal[ absType ] ) )
        if errorInfo:
          errorInfo.write("Invalid date ({}): {}/ {}, last was: {}\n".format( absType, fr, to, lastWas ))
        assert False
      else:
        dVal[ absType ] = to.asValue
      cont.append( (absType, days, fr, to) )
    return rTag, cont

  verbose = opts[ "verbose" ]
  if verbose>=3:
    print("cmd_dump() for:", ioXml, "\nopts:", opts)

  fIn = open( ioXml, "r" )
  if fIn:
    x = fIn.read()
    rTag, cont = processor( ET.fromstring( x ) )
    for line in cont:
      days = int( line[ 1 ] )
      outFile.write("{:3}. days={:<2d} {} to {}\n".format( line[0], days, line[2], line[3] ))
  return 0


#
# cmd_read_raw()
#
def cmd_read_raw (outFile, ioXml, param, basicSample, opts):
  rel = []
  verbose = opts[ "verbose" ]
  lineNr = 0
  for inFile in param:
    cont = open( inFile, "r" ).read().split("\n")
    for rawLine in cont:
      lineNr += 1
      if rawLine.strip()=="":
        continue
      r = simpler_str( rawLine.upper().replace( " OFFICE", "" ).replace( " - ", "_" ).replace( "\t", "  " ) )
      if r.startswith( "~" ):
        ori = simpler_str( r[ 1: ].strip( " \t" ).split( "TAKEN" )[ 0 ] )
        strFromDate = ori.split( " " )[ 0 ]
        date1 = BDate( strFromDate )
        if ori.find( " TO " )>0:
          ran = ori.split( " TO " )
          assert len( ran )==2
          sec = simpler_str( ran[ 1 ] ).split( " " )
          toDate = sec[ 0 ]
          date2 = BDate( toDate )
          rem = simpler_str( " ".join( sec[ 1: ] ) )
          days = date2.diff( date1, 1 )
          bic = ("r", date1.asValue, date2.asValue, simpler_str( ran[ 0 ] )+" "+rem, toDate, days)
        else:
          date2 = BDate( date1.asStr )
          days = 1
          bic = ("s", date1.asValue, date2.asValue, ori, None, days)
        rel.append( bic )
      elif r.find( "~" )>=0:
        if errorInfo:
          errorInfo.write("Bogus line {}: '{}'\n".format( lineNr, r ))
        assert False
      else:
        if errorInfo:
          errorInfo.write("Ignored line {}: '{}'\n".format( lineNr, r ))
  for r in rel:
    if verbose>0:
      print( "Read:", r )
  samplest = basicSample[ 1:-1 ]
  for r in rel:
    strDate1 = str( r[ 1 ] )
    strDate2 = str( r[ 2 ] )
    strOri = r[ 3 ]
    ori = strOri.split( " " )
    absTypeDesc = ori[ 1 ]
    wDays = None
    if absTypeDesc.find("HOME")>=0:
      absType = "HO"
    elif absTypeDesc.find("VAC")>=0:
      absType = "VACATION"
      wDay = float( ori[-1] )
      assert int( wDay )>=1
      wDays = int( wDay )
    else:
      absType = None
    if absType is None:
      if errorInfo:
          errorInfo.write("Ignored original strip ({}): '{}'\n".format( absTypeDesc, strOri ))
    else:
      s = samplest.replace( "@1@", strDate1 ).replace( "@2@", strDate2 )
      s = s.replace( "@3@", absType )
      if wDays is None:
        s = s.replace( "@4@", "" )
      else:
        s = s.replace( "@4@", ' wdays="{}"'.format( wDays ) )
      outFile.write("{}\n".format( s ))
  return 0
        

#
# Main script
#
if __name__ == "__main__":
  import sys
  code = main_run( stdout, stderr, sys.argv[ 1: ] )
  if code is None:
    code = 0
    print("""office_leaves.py command [options] [file(s) ...]

Commands are:
    dump: dump xml
""")
  sys.exit( code )
