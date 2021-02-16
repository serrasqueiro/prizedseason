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
    key_list = opts["keys"].split(":") if opts["keys"] else list()
    keys = tuple(key_list)
    if keys:
        atbl = tabular.Tabular(fname, key_fields=keys)
    else:
        atbl = tabular.Tabular(fname)
    print("Header for", fname, "is:", atbl.get_header())
    print("_all_fields:", atbl.get_fields())
    if atbl.get_msg():
        print("msg:", atbl.get_msg())
    return True


# Main script
if __name__ == "__main__":
    main()
