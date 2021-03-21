# tabular.test.py  (c)2021  Henrique Moreira

"""
Tests tabular.py
"""
# pylint: disable=missing-function-docstring, unused-argument

import sys
import table.tabular as tabular


def main():
    """ Main test! """
    assert runner(sys.stdout, sys.argv[1:]) == 0


def runner(out, args) -> int:
    """ Wrapper to run. """
    code = run_tests(out, args)
    prog = __file__
    if code is None:
        print(f"""{prog} [options] file [...]

Options are:
  -k       Keys to use
""")
        return 0
    return code

def run_tests(out, args: list) -> int:
    """ Run tests.
    You can indicate textual files in the arguments.
    """
    atbl = tabular.Tabular()
    assert atbl.get_msg() == ""
    opts = {
        "keys": None,
        }
    if not args:
        return 0
    param = args
    while param and param[0].startswith("-"):
        if param[0] in ("-k", "--keys"):
            opts["keys"] = param[1]
            del param[:2]
            continue
        return None
    for fname in param:
        is_ok = run_test(out, fname, opts)
        if not is_ok:
            print("Failed test for:", fname)
            return 1
    return 0

def run_test(out, fname, opts) -> bool:
    """ Read text file 'fname'.
    """
    mychr_split = ";"
    aline = open(fname, "r").read(128).split("\n")
    if len(aline) > 1 and "\t" in aline[0]:
        mychr_split = "\t"
    key_list = opts["keys"].split(":") if opts["keys"] else list()
    keys = tuple(key_list)
    if keys:
        print(f"keys={keys}")
        atbl = tabular.Tabular(fname, key_fields=keys, split_chr=mychr_split)
    else:
        atbl = tabular.Tabular(fname, split_chr=mychr_split)
    print("Header for", fname, "is:", atbl.get_header())
    print("_all_fields = get_fields():", atbl.get_fields())
    if atbl.get_msg():
        print("msg:", atbl.get_msg())
    print("field_kinds():", atbl.field_kinds())
    cont = atbl.content()
    is_ok = cont.parse()
    assert is_ok, f"cont.parse() failed: '{fname}'"
    errs = cont.data()["errors"]
    bykey = cont.data()["by-key"]
    print("Tabular() content():", cont)
    print("Content().fields():", cont.fields())
    print("data()['errors']:", errs)
    print("data()['by-key']:", bykey)
    print("All data follows next:")
    idx = 0
    for row in cont.raw_data():
        idx += 1
        print(":::", idx, row)
        there = cont.data()["by-idx"][idx]
        assert row == there, "Unexpected content!"
    #print("by-idx:", cont.data()["by-idx"])
    return True


# Main script
if __name__ == "__main__":
    main()
