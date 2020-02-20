""" stewstick -- basic stock files
"""

from sys import stdout, stdin, stderr
from zexcess import *
from ztable.xdate import *


CO_version="1.00 51"


#
# main()
#
def main (me, outFile, errFile, inArgs):
    if me=="stewstick":   # stewstick.py
        code = stewstick_main( outFile, errFile, inArgs )
    return code


#
# stewstick_main()
#
def stewstick_main (outFile, errFile, inArgs):
    code = None
    verbose = 0   # use 1, or... 9 for more verbose content!
    args = inArgs
    columns = None
    headingNr = 0
    if len( args )<=0:
        return None
    cmd = args[ 0 ]
    param = args[ 1: ]
    # Defaults
    # Options
    while len( param )>0 and param[ 0 ].startswith( "-" ):
        any = False
        if param[ 0 ].find( "-v" )==0:
            any = True
            n = param[ 0 ].count( "v" )
            if n+1!=len( param[ 0 ] ):
                return None
            verbose += n
            del param[ 0 ]
            continue
        if param[ 0 ]=="-c":
            columns = param[ 1 ]
            del param[ :2 ]
            continue
        if param[ 0 ]=="-g": # heading
            headingNr = int( param[ 1 ] )
            del param[ :2 ]
            continue
        return None
    debug = 0 if verbose<3 else 1
    aOpts = (
      "verbose", debug,
      )
    opts = {"verbose": verbose,
            "debug": debug,
            "col": columns,
            "heading-number": headingNr,
            }
    # Run command
    if cmd=="version":
        print("stewstick", CO_version)
        return 0
    if cmd=="test":
        return 0
    if cmd=="dump":
        name = param[ 0 ]
        del param[ 0 ]
        rules = ("open",)
        code = dump(outFile, errFile, name, param, opts, rules)
    return code


#
# dump()
#
def dump (outFile, errFile, name, param, opts, rules):
    assert type(opts)==dict
    onlyOne = True
    verbose = opts[ "verbose" ]
    cols = work_column_defs( opts[ "col" ] )
    headingNr = opts[ "heading-number" ]
    z = ZSheets(name, param)
    sheets, cont = z.contents()
    for pages in cont:
        y = 0
        rowNr = 0
        tbl = ZTable( pages )
        for entry in tbl.cont:
            y += 1
            if y<=headingNr: continue
            rowNr += 1
            cIdx = 0
            for cell in entry:
                cIdx += 1
                cLetter = num_to_column_letters( cIdx )
                s = cell
                if cols and cIdx<len( cols ):
                    d = cols[cIdx]
                    if d=="date":
                        mDate = MsDate(cell)
                        if mDate.jDate:
                            if verbose>0:
                                s = "{}='{}'".format( mDate, cell )
                            else:
                                s = str( mDate )
                    elif d=="time":
                        mTime = MsTime(cell)
                        if verbose>0:
                            s = "{}='{}'".format( mTime, cell )
                        else:
                            s = str( mTime )
                print("{}{}: {}".format( cLetter, y, s ))
            print("...\n")
        if onlyOne:
            break
    return 0


def work_column_defs (s):
    if s is None: return None
    cols = ["."] + s.split(":")
    return cols


#
# Main script
#
if __name__ == "__main__":
    from sys import exit, argv
    me = argv[ 0 ].replace( "\\", "/" ).split( "/" )[ -1 ].replace( ".py", "" )
    code = main( me, stdout, stderr, argv[ 1: ] )
    # See also account.py under packages/processors/
    if code is None:
        print("""stewstick COMMAND [options]

Commands are:
  help
          This help.

  dump    file [sheet]
          Dump xlsx file.

Options are:
  -v      Verbose (or use -vv, -vvv for more verbose).
""")
        code = 0
    assert type( code )==int and code<=255
    exit( code )
