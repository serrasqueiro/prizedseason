# simas.py  (c)2020  Henrique Moreira

"""
  simas -- Read out of SIMAS, contadores agua.

  Compatibility: python 3.
"""

# pylint: disable=invalid-name, unused-argument

import sys
from waxpage.redit import BareText
from tconfig.adate import aDateMaster
from consumption.measure import Measure


def main():
    """ Main run """
    args = sys.argv[ 1: ]
    code = run_simas(sys.stdout, args)
    if code is None:
        print("""
Usage:
	No args!
""")
        code = 0
    assert isinstance(code, int)
    sys.exit(code)


def run_simas (out_file, args):
    """ Basic run """
    code = simas_agua(out_file, args)
    return code


def simas_agua (out_file, args):
    """ SIMAS (agua) """
    param = args
    if param:
        return None
    red = BareText()
    assert red.inEncoding == "ascii"
    red.inEncoding = "iso-8859-1"
    isOk = red.file_reader()
    #print("isOk:", isOk, "; inFilename:", red.inFilename if red.inFilename!="" else "-")
    measured = []
    code = process_input(out_file, red.lines, measured)
    last = 0.0
    x = 0
    for m in measured:
        y = m.measure
        a_day = aDateMaster.calc_MJD(m.calendar)
        isOk = m.calendar.valid_date()
        if not isOk:
            print("Invalid date:", m.when)
            continue
        if last > 0.0:
            deltaDays = a_day - x
            if deltaDays <= 0:
                print("Invalid deltaDays:", deltaDays, "At:", m.when)
            else:
                m3_per_day = (m.measure - last) / float(deltaDays)
                m3_month = m3_per_day * 30
                s = water_formatted(infos=m, delta=deltaDays, litre=m3_month * 1000.0)
                out_file.write("{}\n".format(s))
        last = y
        x = a_day
    return code


def process_input (out_file, lines, measured, action=""):
    """ Text input parser. """
    code = 0
    juice = []
    for el in lines:
        s = el.strip()
        if s.find( "Data" ) == 0:
            continue
        #print("{", el, "}")
        if len( s )>10:
            date = s[ :10 ]
            rest = s[ 11: ].strip()
            if rest.endswith( "Empresa" ):
                rest += " -"
            baga = rest.replace( '\t', ' ' ).split( ' ' )
            isOk = len( baga )==4
            if not isOk:
                print("Failed: date={"+date+"}", "baga:", baga)
                return 1
            juice.append( (date, "m3", baga[ 1 ], "who", baga[ 2 ]) )
    for j in juice:
        m = Measure( j[0] )
        m.measure = float( j[2] )
        m.newFormat = "{:0.0f}"
        m.comment = j[4]
        #print("m:", m)
        measured.append( m )

    if action == "dump":
        for m in measured:
            print( m )
            #out_file.write(' '.join( j ) + "\n")
    return code


def water_formatted(infos, delta, litre):
    """ Line formatted to show m3 of water """
    assert isinstance(litre, float)
    m3 = litre / 1000.0
    s = f"{infos}.m3, days: {delta:5d} {m3:10.3f} m3/month"
    #s += " |"
    #s += str(dir(date)) + "\n"
    return s


#
# Main script
#
if __name__ == "__main__":
    main()
