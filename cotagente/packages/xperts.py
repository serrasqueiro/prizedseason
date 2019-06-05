# xperts.py  (c)2019  Henrique Moreira (part of 'cotagente')

"""
  Process html from xperteleven...etc.

  Compatibility: python 2 and 3.
"""

from fsimpler import Tablex, de_split, de_where


#
# test_xperts()
#
def test_xperts (aOutFile, inArgs):
  errFile = sys.stderr
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
# CLASS Teams
#
class Teams:
  def __init__ (self):
    self.init_teams()


  def init_teams (self):
    self.quads = {}


  def add_squad (self, squad):
    self.quads[ squad.id ] = squad


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
  code = test_xperts( sys.stdout, args )
  assert code==0
  sys.exit( code )
