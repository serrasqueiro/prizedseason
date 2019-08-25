# team_temp_values.py  (c)2019  Henrique Moreira (part of 'trisconta')

"""
  team_temp script works team values

  Compatibility: python 2 and 3.
"""

from sys import stdin, stdout, stderr
import xml.etree.ElementTree as ET
import os.path

errorInfo = stderr
#errorInfo = None  # uncomment this line to avoid too much verbose output


#
# team_temp() -- main run
#
def team_temp (outFile, errFile, inArgs):
  code = None
  try:
    cmd = inArgs[ 0 ]
  except:
    return None
  assert cmd.startswith( "-" )==False
  param = inArgs[ 1: ]
  verbose = 0
  doDump = False
  doAny = True
  assert errFile==stderr
  while len( param )>0 and doAny:
    doAny = False
    if param[ 0 ].startswith( "-v" ):
      doAny = True
      verbose += param[ 0 ].count( "v" )
      del param[ 0 ]
      continue
    if param[ 0 ].startswith( "--dump-xml" ):
      doAny = True
      doDump = True
      del param[ 0 ]
      continue
  baseDir = None
  opts = {"verbose":verbose,
          "dump-xml":doDump,
          "base-dir":baseDir,
          }
  if cmd=="misc":
    return misc_help()
  if len( param )<=0:
    param = ["--stdin"]
  else:
    assert param[ 0 ].startswith( "-" )==False
  tuples = []
  for p in param:
    if p=="--stdin":
      name = None
      inFile = stdin
    else:
      try:
        inFile = open( p, "r" )
      except FileNotFoundError:
        errFile.write("Cannot open: " + p + "\n")
        return 2
      name = p
      if baseDir is None:
        baseDir = os.path.dirname( p )
    cont = inFile.read()
    if name is not None:
      inFile.close()
    tuple = (name, cont)
    tuples.append( tuple )
  if baseDir is not None:
    opts[ "base-dir" ] = baseDir
  if cmd=="text-dump":
    code = processor( tuples, opts )
  if code is None:
    print("Invalid usage.")
    return None
  if verbose>0:
    bDir = baseDir if baseDir!="" else "."
    stderr.write("processor() returned: {}, base-dir: {}\n".format( code, bDir ))
  return code


#
# misc_help()
#
def misc_help ():
  misc1 = """
cat raw_zzero.lst.txu |tr ' ' _ | xargs -n 4|awk '{print $3,$2}' | ssed subst 'equipa.php?id=' ""  | tr ' ' \\011 | tr _ ' '
"""
  misc2 = """
cat raw_zzero.tsv.txt | grep -v ^"#" | tr \\011 @ | tr ' ' _ | tr @ \\012 | xargs -n 3 | tr ' ' ';' | tr _ ' '
"""
  print("To convert zzero HTML into a tab separated list:\n\t# {}\n".format( misc1[ 1:-1 ] ))
  print("To convert existing tab separated list (...tsv.txt)\n into semi-colon separated list:\n\t# {}\n".format( misc2[ 1:-1 ] ))
  return 0


#
# processor()
#
def processor (tuples, opts):
  outFile = stdout
  verbose = opts[ "verbose" ]
  sampleName = tuples[ 0 ][ 0 ]
  sampleContent = tuples[ 0 ][ 1 ]
  root = ET.fromstring( sampleContent )
  rootTag = root.tag      # e.g. 'orderset'
  if opts[ "dump-xml" ]:
    #lines = ET.tostring(root).decode("ascii").replace("\t", "  ").split( "\n" )
    lines = basic_ascii_tree( ET.tostring(root) )
    for line in lines:
      s = line.strip()
      outFile.write("{}\n".format( s ))
    return 0
  if verbose>0:
    basic_skel( root )
  return 0


#
# basic_ascii_tree()
#
def basic_ascii_tree (binInfo):
  lines = binInfo.decode("ascii").replace("\t", "  ").split("\n")
  return lines


#
# basic_skel()
#
def basic_skel (treeRoot):
  root = treeRoot
  xsdName = root.tag.replace( "{", "}" ).split( "}" )[ -1 ]
  if xsdName=="TeamLists":
    idx = 1
    for el in root:
      a = el.attrib
      myid = int( a[ "myid" ] )
      name = a[ "name" ]
      team_tempContent = {}
      for sub in el:
        tag = tag_unq( sub.tag )
        text = sub.text
        team_tempContent[ tag ] = text
      try:
        anoFundacao = team_tempContent[ "anofundacao" ]
      except:
        anoFundacao = ""
      try:
        guiLabel = team_tempContent[ "longname" ]
      except:
        guiLabel = ""
      if guiLabel=="":
        guiLabel = human_gui( name )
      print("{}: {} ; fundado em {}; long-name='{}'".format( myid, name, anoFundacao, guiLabel ))
      if myid!=idx:
        if errorInfo is not None:
          errorInfo.write("Bogus index for {}: {}\n".format( name, myid ))
      assert myid==idx
      assert int( anoFundacao )>=1000
      idx += 1
    pass
    return 0
  rName = root.attrib[ "name" ]
  isLegacyBCB = rName=="TeamList"
  if isLegacyBCB:
    rTag = root.tag
    assert rTag=="enumeration"
    root = treeRoot[ 1: ]
    idx = 0
    for e in root:
      a = e.attrib
      val = int( a[ "myid" ] )
      hasGUI = False
      try:
        guiLabel = "'{}'".format( e.findall("longname")[ 0 ].text )
        hasGUI = True
      except:
        guiLabel = human_gui( a[ "name" ] )
        print("{}:".format(idx), a, "longname:", guiLabel)
      assert val==idx
      idx += 1
    return 0
  if root is not None:
    idx = 0
    for child in root:
      idx += 1
      print("{}:".format( idx ), child.tag, child.attrib)
      bID = int( child.attrib["bID"] )
      bName = child.attrib["bName"]
      assert idx==bID
      for u in child.iter("userinfo"):
        for el in u:
          #print("el:", el, el.attrib, "userinfo tag:", "{}.{} '{}'".format(bName, el.tag, el.text))
          print("userinfo (bID: bName.tag 'text'):", "{}: {}.{} '{}'".format(bID, bName, el.tag, el.text))
          for userInfoEl in el.findall("."):
            ignore = userInfoEl.tag.find( "tmf" )==0
            if not ignore:
              #print("userInfoEl:", userInfoEl, userInfoEl.attrib, "tag:", userInfoEl.tag)
              print("userInfoEl, tag:", userInfoEl.tag)
  return 0


#
# tag_unq()
#
def tag_unq (tag):
  assert type( tag )==str
  return tag[tag.find("/TeamLists") + len("/TeamLists") + 1:]


#
# human_gui()
#
def human_gui (s):
  idx = 0
  res = ""
  for c in s:
    toAdd = ""
    idx += 1
    p = c.upper()
    if idx==1:
      toAdd = p
    else:
      if c==p:  # upper-case char
        toAdd = " "
      toAdd += c
    res += toAdd
  return res


#
# Main script
#
if __name__ == "__main__":
  import sys
  code = team_temp( stdout, stderr, sys.argv[ 1: ] )
  if code is None:
    code = 0
    print("""team_temp_values.py command [options] [file(s) ...]

Commands are:
    text-dump: dump teams xml in text form

    misc: show miscelaneous help
""")
  sys.exit( code )
