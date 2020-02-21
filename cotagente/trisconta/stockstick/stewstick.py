""" stewstick -- basic stock files
"""

# pylint: disable=unused-argument, invalid-name


from sys import stdout, stderr
from zexcess import ZSheets, ZTable, num_to_column_letters
from ztable.xdate import MsDate, MsTime

CO_VERSION = "1.00 53"


def run_main(my_path, args):
    """
    Main script/ caller.
    :param my_path: the entire argv 0
    :param args: arguments
    :return: None (wrong arguments) or an error-code.
    """
    me = my_path.replace("\\", "/").split("/")[-1].replace(".py", "")
    code = main(me, stdout, stderr, args)
    return code


def main(me, outFile, errFile, inArgs):
    """
    Main program
    :param me:
    :param outFile: output stream
    :param errFile: error stream
    :param inArgs: input args
    :return:
    """
    code = None
    if me == "stewstick":   # stewstick.py
        code = stewstick_main(outFile, errFile, inArgs)
    return code


#
# stewstick_main()
#
def stewstick_main(outFile, errFile, inArgs):
    """
    Main script run.
    """
    code = None
    verbose = 0   # use 1, or... 9 for more verbose content!
    args = inArgs
    columns = None
    headingNr = 0
    if args == []:
        return None
    cmd = args[0]
    param = args[1:]
    # Defaults
    # Options
    while len(param) > 0 and param[0].startswith("-"):
        if param[0].find("-v") == 0:
            n = param[0].count("v")
            if n + 1 != len(param[0]):
                return None
            verbose += n
            del param[0]
            continue
        if param[0] == "-c":
            columns = param[1]
            del param[:2]
            continue
        if param[0] == "-g":  # heading
            headingNr = int(param[1])
            del param[:2]
            continue
        return None
    debug = 0 if verbose < 3 else 1
    opts = {"verbose": verbose,
            "debug": debug,
            "col": columns,
            "heading-number": headingNr,
            }
    # Run command
    if cmd == "version":
        print("stewstick", CO_VERSION)
        return 0
    if cmd == "test":
        return 0
    if cmd == "dump":
        name = param[0]
        del param[0]
        rules = ("open",)
        code = dump(outFile, errFile, name, param, opts, rules)
    return code


def dump(outFile, errFile, name, param, opts, rules):
    """
    Dump xls file.
    :param outFile: output stream
    :param errFile: error stream
    :param name: filename
    :param param: parameters
    :param opts: other options
    :param rules: ToDo
    :return:
    """
    assert isinstance(opts, dict)
    code = 0
    debug = opts["debug"]
    onlyOne = True
    z = ZSheets(name, param)
    _, cont = z.contents()	# sheets and contents
    for pages in cont:
        code = dump_table(outFile, errFile, pages, param, opts, rules, debug)
        if onlyOne:
            break
    return code


def dump_table(outFile, errFile, pages, param, opts, rules, debug=1):
    """
    Dump one table.
    :param outFile: output stream
    :param errFile:  error stream
    :param pages: pages to show
    :param param: any other parameter
    :param opts: options
    :param rules: Rules
    :return: int, an error-code
    """
    cols = work_column_defs(opts["col"])
    headingNr = opts["heading-number"]
    y = 0
    rowNr = 0
    tbl = ZTable(pages)
    for entry in tbl.cont:
        y += 1
        if y <= headingNr:
            continue
        rowNr += 1
        cIdx = 0
        dumped = 0
        for cell in entry:
            cIdx += 1
            cLetter = num_to_column_letters(cIdx)
            cell_name = "{}{}".format(cLetter, y)
            s = cell
            if cols and cIdx < len(cols):
                d = cols[cIdx]
                if d == "date":
                    mDate = MsDate(cell)
                    if mDate.jDate:
                        if debug > 0:
                            s = "{}='{}'".format(mDate, cell)
                        else:
                            s = str(mDate)
                elif d == "time":
                    mTime = MsTime(cell)
                    if debug > 0:
                        s = "{}='{}'".format(mTime, cell)
                    else:
                        s = str(mTime)
            outFile.write("{}: {}\n".format(cell_name, s))
            dumped += 1
        if dumped > 0:
            outFile.write("...\n\n")
    return 0


def work_column_defs(s):
    """
    Work on those columns, defined by user arguments.
    """
    if s is None:
        return None
    cols = ["."] + s.split(":")
    return cols


#
# Main script
#
if __name__ == "__main__":
    import sys
    from sys import argv
    CODE = run_main(argv[0], argv[1:])
    if CODE is None:
        print("""stewstick COMMAND [options]

Commands are:
  help
          This help.

  dump    file [sheet]
          Dump xlsx file.

Options are:
  -v      Verbose (or use -vv, -vvv for more verbose).
""")
        CODE = 0
    assert isinstance(CODE, int) and CODE <= 255
    sys.exit(CODE)
