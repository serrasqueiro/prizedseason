""" stewstick -- basic stock files
"""

# pylint: disable=unused-argument, invalid-name, no-else-return


from sys import stdout, stderr
from zexcess import ZSheets, ZTable, num_to_column_letters
from zrules import ZRules, cell_string, work_column_defs, keys_from_str
from ztable.ztables import Tabular
from ztable.xdate import MsDate
from zlatin import flow_list, numbered_list, cur_format

CO_VERSION = "1.00 54"


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
    ops = []
    verbose = 0   # use 1, or... 9 for more verbose content!
    args = inArgs
    columns = None
    headingNr = 0
    if args == []:
        return None
    cmd = args[0]
    param = args[1:]
    # Defaults
    opt_rules = ""
    out_name = None
    strict_cols = False
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
        if param[0] == "-k":
            opt_rules = param[1]
            del param[:2]
            continue
        if param[0] in ("-o", "--out"):
            out_name = param[1]
            del param[:2]
            continue
        if param[0] in ("-s", "--strict"):
            strict_cols = True
            del param[0]
            continue
        return None
    debug = 0 if verbose < 3 else 1
    opts = {"verbose": verbose,
            "debug": debug,
            "col": columns,
            "strict-cols": strict_cols,
            "heading-number": headingNr,
            }
    # Common parameters
    rules = ZRules(keys_from_str(opt_rules))
    if out_name is not None:
        outFile = open(out_name, "w")
    # Run command
    if cmd == "version":
        assert out_name is None
        print("stewstick", CO_VERSION)
        return 0
    elif cmd == "test":
        assert out_name is None
        if opt_rules:
            rules.dump()
        return 0
    elif cmd == "dump":
        name = param[0]
        del param[0]
        code = dump(outFile, errFile, name, param, opts, rules)
    elif cmd == "textual":
        name = param[0]
        del param[0]
        code = dump_textual_table(outFile, errFile, name, param, opts, rules)
    elif cmd == "slim":
        name = param[0]
        del param[0]
        assert len(param) <= 1
        code = dump_textual_table(None, errFile, name, [], opts, rules)
        if verbose > 0:
            print(":".join(rules.header))
        if code == 0:
            ops = slim_stocks(rules.content, param, opts, rules)
        for _, s_row in ops:
            outFile.write("{}\n".format(s_row))
    tabular = Tabular(out_name, outFile)
    tabular.rewrite()
    if verbose > 0:
        if out_name:
            if tabular.content_size >= 0:
                print("Wrote {}: {} octets".format(out_name, tabular.content_size))
            else:
                print("Wrote {}".format(out_name))
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


def dump_table(outFile, errFile, pages, param, opts, rules, debug=0):
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
                s = cell_string(cell, d, "-", debug)
            outFile.write("{}: {}\n".format(cell_name, s))
            dumped += 1
        if dumped > 0:
            outFile.write("...\n\n")
    return 0


def dump_textual_table(outFile, errFile, name, param, opts, rules, debug=0):
    """
    Dump xcel to textual file.
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
    assert isinstance(opts, dict)
    verbose = opts["verbose"]
    z = ZSheets(name, param)
    sheets, cont = z.contents()
    assert len(sheets) == len(cont)
    idx_sheet = 0
    for pages in cont:
        y, rowNr = 0, 0
        lines, suppressed = 0, 0
        tbl = ZTable(pages, strict_charset="latin-like")
        if verbose > 0:
            int_name, ws_xml, ref_name = sheets[idx_sheet]
            print("{}: {} ({})".format(ref_name, int_name, ws_xml))
        idx_sheet += 1
        for entry in tbl.cont:
            y += 1
            if y <= headingNr:
                rules.set_heading(entry)
                continue
            rowNr += 1
            cIdx = 0
            row = []
            for cell in entry:
                cIdx += 1
                s = cell
                if cols and cIdx < len(cols):
                    d = cols[cIdx]
                    s = cell_string(cell, d, "-")
                row.append(s)
            do_show = do_show_row(row, rules)
            if do_show:
                lines += 1
                pre = ""
                if opts["strict-cols"]:
                    s_row = filter_columns(row, rules, cols)
                    if debug > 0:
                        print("s_row:", numbered_list(s_row))
                else:
                    s_row = row
                if outFile is None:
                    part = []
                    for a in s_row:
                        part.append(a)
                    rules.content.append(part)
                else:
                    for a in s_row:
                        outFile.write("{}{}".format(pre, a))
                        pre = ";"
                    outFile.write("\n")
            else:
                suppressed += 1
        if verbose > 0:
            print("Lines: {}, suppressed: {}".format(lines, suppressed))
    return 0


def slim_stocks(cont, param, opts, rules, debug=0):
    """
    Show text tabular stocks
    :param outFile: output stream
    :param cont: content
    :param param: parameters
    :param opts: options
    :param rules: Rules
    :param debug: int, debug
    :return: list, operations (by date)
    """
    ops = []
    y = 0
    y_shown = 0
    verbose = opts["verbose"]
    if param == []:
        what = None
    else:
        what = param[0]
    for row in cont:
        y += 1
        # 1:m; 2:2020-02-14; 3:9:45; 4:GALP; 5:''; 6:''; 7:-150; 8:14.01; 9:EUR; 10:-2101.5
        w = row[0]
        if debug > 0:
            print("y={}, w='{}'".format(y, w))
            print(">>>\n" + flow_list(row, "\t") + "<<<")
        if what is None or what == w:
            y_shown += 1
            s_idx = "" if verbose <= 0 else "{}:\t".format(y_shown)
            s_date = row[1]
            ms = MsDate(s_date)
            tm = row[2] if len(row[2]) >= 5 else "0" + row[2]
            date_time = s_date+" "+tm
            rest = row[3:]
            s_name, _, _, quant, s_per, coin, s_loc_val = rest
            per_stock = float(s_per) if s_per not in ("", "-") else 0.0  # per stock value
            per = round(per_stock, 4)
            loc_val = round(float(s_loc_val), 3)
            weekday = ms.weekday_str()
            diff = round(quant * per, 3) - loc_val
            tic = "" if diff == 0.0 else " diff={:.3f}=({}*{})".format(diff, quant, per)
            if tic == "" and coin != "EUR":
                tic = coin
            if verbose > 0:
                s = "{}{} {} {:7} {:_<13.12} {} val: {}{}".format(
                    s_idx, weekday, date_time, quant, s_name,
                    cur_format(per), cur_format(loc_val), tic)
            else:
                if what is None:
                    s_idx = w + ": "
                else:
                    s_idx = ""
                s = "{}{} {} {:7} {:_<13.12} {} val: {}".format(
                    s_idx, weekday, date_time, quant, s_name,
                    cur_format(per), cur_format(loc_val, tail_blank=None))
            ops.append(((date_time, s_name, quant, per), s))
            assert coin == "EUR"
    if len(ops) >= 2:
        if ops[0][0][0] > ops[-1][0][0]:
            # Invert list: usually does, as input often starts with latest date first
            return invert_list(ops)
    return ops


def do_show_row(row, rules):
    """
    Checks whether row is to be shown.
    :param row: the list of cells
    :param rules: Rules, including the key columns
    :return: bool, whether row is relevant to be shown
    """
    do_show = rules.key_columns == []
    if do_show:
        return True
    if row == []:
        return False
    all_empty = True
    for k_str in rules.key_columns:
        if not all_empty:
            break
        m_col = rules.header_hash.get(k_str)
        if m_col is not None:
            m_col -= 1
            is_empty = row[m_col] in ("", "-",)
            if not is_empty:
                all_empty = False
                break
    do_show = not all_empty
    return do_show


def filter_columns(row, rules, cols, debug=0):
    """
    Filter columns based on rules.
    :param row: the entire row
    :param rules: Rules
    :param cols: columns adopted
    :param debug: debug
    :return: list, the resulting columns from 'row'
    """
    assert isinstance(rules, ZRules)
    if cols is None:
        columns = ["."] + rules.header
    else:
        columns = cols
    idx, len_col = 1, len(columns)
    if debug > 0:
        print("\nfilter_columns: {}\n\t{}".format(numbered_list(row), numbered_list(columns)))
    res = []
    for cell in row:
        if idx < len_col:
            col_name = columns[idx]
        else:
            col_name = ""
        if col_name:
            res.append(cell)
        idx += 1
    return res


def invert_list(ops):
    """
    Invert list
    :param ops: list of operations (well, just a list!)
    :return: list, the inverted order list
    """
    assert isinstance(ops, list)
    idx = len(ops)
    res = []
    while idx > 0:
        idx -= 1
        res.append(ops[idx])
    return res


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
  test    Show arguments parsed
  
  dump    file [sheet]
          Dump xlsx file.

  textual file [sheet]
          Dump xlsx file as text.
          
  slim    file [sheet]
          Dump xlsx file as text, simple stocks.

Options are:
  -v      Verbose (or use -vv, -vvv for more verbose).
""")
        CODE = 0
    assert isinstance(CODE, int) and CODE <= 255
    sys.exit(CODE)
