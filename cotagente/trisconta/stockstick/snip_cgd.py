#-*- coding: utf-8 -*-
# snip_cgd.py  (c)2022  Henrique Moreira

""" CGD comprovativo.txu/ mov.lst reader

Command:
	cmd = (see below)
==> comprovativo.txu <==
# Conta: ...

==> mov.lst <==
#key;expl

"""
# cmd:
#	head -1 comprovativo.txu mov.lst | sed 's/^# \(.*:\)\(.*\)/# \1 .../'

# pylint: disable=missing-docstring

import sys
import datetime
import os.path
from os import environ
import table.tabular


def main():
    """ Main function """
    run(sys.argv[1:])

def run(args:list) -> int:
    """ Run script """
    opts = {
        "verbose": 0,
        "config-path": environ.get("FINACONTA"),
    }
    fname, mov_fname = "comprovativo.txu", "mov.lst"
    out = sys.stdout
    param = args
    if param and param[0] == "-v":
        param, opts["verbose"] = param[1:], 1
    if opts["config-path"] is not None:
        if len(param) == 1 and "/" not in param[0].replace("\\", "/"):
            param = [os.path.join(os.path.dirname(opts["config-path"]), param[0])]
    if not param:
        param = [""]
    for item in param:
        code = dump_pair(out, item, (fname, mov_fname), opts)
        if code:
            print(f"Error code={code}, item: {item}")


def dump_pair(out, adir:str, params:tuple, opts:dict) -> int:
    fname, mov_fname = params
    verbose = opts["verbose"]
    if adir:
        fname = os.path.join(adir, fname)
        mov_fname = os.path.join(adir, mov_fname)
    if verbose > 0:
        print("# Dump:", fname)
    return dump_stuff(out, fname, mov_fname, opts)


def dump_stuff(out, fname, mov_fname, opts:dict) -> int:
    """ Interesting dump itself! """
    assert opts
    s_head = "#mdate;vdate;desc;debt;cred;acc;eq;hint"
    # atbl.get_fields() = ('mdate', 'vdate', 'desc', 'debt', 'cred', 'acc', 'eq', 'hint')
    atbl = table.tabular.Tabular(fname, split_chr=";", ref_str=s_head)
    #print("# atbl:", atbl)
    try:
        mov = table.stable.STableKey(mov_fname, unique_k2=False)
    except FileNotFoundError:
        mov = None
    if mov is None:
        mov_info_keys = tuple()
    else:
        mov.get_keys()
        mov_info_keys = mov.keyval[0]
    assert mov_info_keys is not None
    # Row iteration
    for row in atbl.get_rows():
        if row.startswith("#"):
            continue
        assert row
        spl = row.split(";")
        mdate, vdate = ymdate(spl[0]), ymdate(spl[1])
        diff_date = days(to_date(mdate), to_date(vdate))
        #print(f"\n{diff_date} days", mdate, spl[2:])
        assert -30 < diff_date < 90, f"Too much difference ({diff_date}days): {spl}"
        fields, spl = atbl.get_fields()[2:], spl[2:]
        dct = row_dict(fields, spl)
        mkey = f"{mdate},{dct['debt']},{dct['cred']},{dct['acc']}"
        #print(mdate, dct)
        astr = f"{mdate} {dct['debt']:>12} {dct['cred']:>12} {dct['acc']:>12} {dct['desc']}"
        hint = mov_info_keys.get(mkey) if mov_info_keys is not None else None
        if hint is not None:
            astr += " @ " + hint
        if out:
            out.write(astr + "\n")
    return 0


def ymdate(astr) -> str:
    if not astr:
        return ""
    if len(astr) < 10:
        return astr
    return astr[6:] + "." + astr[3:5] + "." + astr[0:2]

def to_date(iso_date:str, fmt:str="."):
    #dttm = datetime.datetime.strptime("2021-12-30", "%Y-%m-%d")
    if fmt == ".":
        date_format = "%Y.%m.%d"
    else:
        date_format = "%Y-%m-%d"
    dttm = datetime.datetime.strptime(iso_date, date_format)
    return dttm

def days(d_t0, d_t1):
    return (d_t0 - d_t1).days


def row_dict(fields:tuple, values:list):
    """ Returns the dictionary for a textual row
    """
    dct = {}
    for idx, name in enumerate(fields):
        assert name not in dct, "Duplicate field names!"
        dct[name] = values[idx]
    return dct


if __name__=="__main__":
    main()
