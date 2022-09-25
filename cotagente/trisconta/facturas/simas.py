#!/usr/bin/python3
#-*- coding: ISO-8859-1 -*-
#
# simas.py  (c)2020, 2022  Henrique Moreira

"""
  simas -- Read out of SIMAS, contadores agua.

  Compatibility: python 3.
"""

# pylint: disable=missing-function-docstring, invalid-name

import sys
from waxpage.redit import BareText
from tconfig.adate import aDateMaster
from consumption.measure import Measure


def main():
    """ Main run """
    args = sys.argv[1:]
    code = run_simas(sys.stdout, args)
    if code is None:
        print("""
Usage:
	No args!
""")
        code = 0
    assert isinstance(code, int)
    sys.exit(code)


def run_simas(out_file, args):
    """ Basic run """
    code = simas_agua(out_file, args)
    return code


def simas_agua(out_file, args):
    """ SIMAS (agua) """
    param = args
    if param:
        return None
    red = BareText()
    assert red.inEncoding == "ascii"
    red.inEncoding = "iso-8859-1"
    is_ok = red.file_reader()
    #print("is_ok:", is_ok, "; inFilename:", red.inFilename if red.inFilename!="" else "-")
    measured = []
    code = process_input(out_file, red.lines, measured, action="")
    last = 0.0
    x = 0
    if len(measured) > 1:
        one = measured[0].calendar
        two = measured[1].calendar
        rev = two < one
        if rev:
            measured.reverse()
    for m in measured:
        y = m.measure
        a_day = aDateMaster.calc_MJD(m.calendar)
        is_ok = m.calendar.valid_date()
        if not is_ok:
            print("Invalid date:", m.when())
            continue
        if last > 0.0:
            delta_days = a_day - x
            if delta_days <= 0:
                print("Invalid delta_days:", delta_days, "At:", m.when())
            else:
                m3_per_day = (m.measure - last) / float(delta_days)
                m3_month = m3_per_day * 30
                s = water_formatted(infos=m, delta=delta_days, litre=m3_month * 1000.0)
                out_file.write(f"{s}\n")
        last = y
        x = a_day
    return code


def process_input(out_file, lines, measured, action=""):
    """ Text input parser. """
    code = 0
    juice = []
    for line in lines:
        s = line.strip()
        if s.find("Data") == 0:
            continue
        if s.count(",") > 1:
            s = s.replace(",", "\t")
        if len(s) > 10:
            date = s[:10]
            rest = s[11:].strip()
            if rest.endswith(("Empresa", "Leitor")):
                rest += " -"
            baga = rest.replace('\t', ' ').split(' ')
            is_ok = len(baga) == 4
            msg = f"Failed: date={date}, baga: {baga}; expected 4 elems, got {len(baga)}"
            if not is_ok:
                print(msg)
                return 1
            item = {"date": date, "m3": baga[1], "who": baga[2]}
            juice.append(item)
    for item in juice:
        m = Measure(item["date"])
        m.measure = measured_m3(item["m3"])
        m.newFormat = "{:0.0f}"
        m.comment = item["who"]
        measured.append(m)
    if action == "dump":
        for item in measured:
            out_file.write(f"{item}\n")
    return code


def measured_m3(astr:str) -> float:
    val = float(astr.replace(",", "."))
    assert val > 0.0
    return val


def water_formatted(infos, delta, litre):
    """ Line formatted to show m3 of water """
    assert isinstance(litre, float)
    m3_ = litre / 1000.0
    astr = f"{infos}.m3, days: {delta:5d} {m3_:10.3f} m3/month"
    #s += " |"
    #s += str(dir(date)) + "\n"
    return astr


#
# Main script
#
if __name__ == "__main__":
    main()
