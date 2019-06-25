# xperts.py  (c)2019  Henrique Moreira (part of 'cotagente')

"""
  Process html from xperteleven...etc.

  Compatibility: python 2 and 3.
"""

import fsimpler
from fsimpler import Tablex, de_split, de_where, re_join


#
# test_xperts()
#
def test_xperts (aOutFile, errFile, inArgs):
  cmd = None
  param = inArgs
  code = 0
  verbose = 0
  doAny = True
  outFile = aOutFile
  if len( param )>0:
    cmd = param[ 0 ]
    del param[ 0 ]
    assert cmd.startswith( "-" )==False
  while len( param )>0 and doAny:
    doAny = False
    if param[ 0 ].find( '-v' )==0:
      doAny = True
      verbose += param[ 0 ].count( 'v' )
      del param[ 0 ]
      continue
    if param[ 0 ]=='-o':
      doAny = True
      outFile = open( param[ 1 ], "w" )
      del param[ :2 ]
      continue
  opts = ("verbose", verbose,
          "output_stream", outFile,
          )
  teams = Teams()
  if cmd:
    if cmd=="squad":
      code = run_squad( cmd, param, opts )
      return code
    if cmd=="calendar":
      sqs = []
      code = run_calendar( outFile, param, opts, sqs )
      for sq in sqs:
        print("Squad: '{}', has id: {}".format( sq.name, sq.id ), end=";")
        isOk = teams.add_squad( sq )
        print(" NEW" if isOk else "")
      return code
    print("cmd:", cmd)
  # Do tests
  for fileName in param:
    if fileName=='--stdin':
      name = ""
    else:
      name = fileName
    rf = Tablex( name )
    if not rf.read_stream():
      code = 2
      errFile.write("Uops reading: " + name + "\n")
    else:
      rf.add_lines( "latin-1" )
      for a in rf.lines:
        if verbose>=3:
          print(":::", a)
        b = a.strip()
        pos = b.find( 'Hyperlink16" href="team.aspx?teamid=' )
        hit = pos>0 and b.find( "<a id=" )>=0
        if hit:
          spl = de_split( b, ('=', '&', '"', '?', '<', '>'), True )
          pos = de_where( spl, "teamid" )
          if pos>=0:
            names = spl[ -5: ]
            while len( names )>0 and len( names[ 0 ] )>0 and not names[ 0 ][ 0 ].isalpha():
              del names[ 0 ]
            name = names[ 0 ]
            if verbose>0:
              print("")
              print( spl )
            print( spl[pos], spl[pos+1], name )
            sq = Squad( name )
            sq.set_id( spl[ pos+2 ] )
            print(sq)
          else:
            errFile.write("Strange: '"+b+"'\n")
  if outFile!=aOutFile:
    outFile.close()
  return code


#
# run_squad()
#
def run_squad (cmd, param, opts):
  verbose = opts[ 1 ]
  prefs = ("Realfornelos",
           )
  """
Squad examples:

Realfornelos:
	http://xperteleven.com/players.aspx?dh=1&TeamID=1845332&Boost=0&plang=EN
ASL:
	http://xperteleven.com/players.aspx?dh=2&TeamID=1846316&Boost=0&plang=EN
Indefectiveis:
	http://xperteleven.com/players.aspx?TeamID=1218537&Boost=0&dh=1&plang=EN

Matches:
  http://xperteleven.com/games.aspx?Sel=O&TeamID=1845332&dh=1&plang=EN
  """
  print("Squads:", prefs)
  print("param:", param)
  return 0


#
# run_calendar()
#
def run_calendar (outFile, param, opts, sqs):
  # http://xperteleven.com/fixture.aspx?Lid=414&Lnr=115&dh=1&plang=EN
  verbose = int( opts[ 1 ] )
  for p in param:
    print("PARAM:", p)
  print("opts:", opts)
  for fileName in param:
    name = fileName
    rf = Tablex( name )
    rf.read_stream()
    rf.add_lines( "latin-1" )
    for a in rf.lines:
      pos = a.find( 'ctl00_cphMain_dgFixture' )
      if pos>0:
        b = a[ pos-1: ]
        spl = de_split( b, ("<", ">", '&') )
        fsimpler.list_rid( spl, ("", "amp;") )
        #fsimpler.list_rid( spl, "amp;" )
        seemTeam = len( spl )==3 and spl[ -1 ]=="/a"
        team = de_split( spl[ 0 ], "?" ) if (seemTeam and spl[ 0 ].find( "?teamid=" )>0) else None
        if verbose>=3:
          for s in spl:
            print("Dbg:", "notTeam" if team is None else re_join(';\n',team), "[{}]".format( s ))
          print("\n")
        if team is not None:
          id = spl[ 0 ].split( "=" )[ -1 ]
          name = spl[ 1 ]
          sq = Squad( name )
          sq.set_id( id )
          sqs.append( sq )
  return 0


#
# CLASS Teams
#
class Teams:
  def __init__ (self):
    self.init_teams()


  def init_teams (self):
    self.quads = {}


  def add_squad (self, squad):
    added = squad.id not in self.quads
    self.quads[ squad.id ] = squad
    return added


#
# CLASS Squad
#
class Squad:
  def __init__ (self, name, teamID=0):
    assert type( name )==str
    self.name = name
    self.id = teamID


  def set_id (self, idStr):
    if type( idStr )==str:
      i = int( idStr )
    else:
      assert type( idStr )==int
      i = idStr
    self.id = i


  def __str__ (self):
    s = "{} (#{})".format( self.name, self.id )
    return s


#
# Test suite
#
if __name__ == "__main__":
  import sys
  args = sys.argv[ 1: ]
  code = test_xperts( sys.stdout, sys.stderr, args )
  assert code==0
  sys.exit( code )
