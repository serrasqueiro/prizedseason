# -*- coding: utf-8 -*-
# poco.test.py  (c)2020  Henrique Moreira

"""
Test poco.py
"""

# pylint: disable=invalid-name

import sys
from hookpdf.poco import readerControl, latinfy


def main():
    """ Main function """
    code = run_test(sys.stdout, sys.stderr, sys.argv[1:])
    assert isinstance(code, int)
    assert code <= 127
    sys.exit(code)


def run_test(out, err, args):
    """ Run test, either basic or the full script. """
    if args:
        if args[0] == ".":
            return simple_test(out, err, args[1:])
    return main_script(out, err, args)


def simple_test(out, err, args):
    """ Simple test! """
    code = 0
    kind = "textual"
    is_utf = readerControl.is_encoding_utf8()
    readerControl.set_output_latin1()
    param = args
    if param:
        name = param[0]
        del param[0]
    else:
        name = None
    assert param == []
    if name:
        code, cont = readerControl.pdf_text(name, kind, err)
    else:
        cont = pre_strings(err)
    err.write("UTF-8 default encoding? {}\n".format(is_utf))
    err.write("cont size={}, type: {}\n".format(len(cont), type(cont)))
    for line in cont:
        out.write(line + "\n")
    return code


def main_script(out, err, args):
    """ 'poco' script itself
    """
    code = main_poco(out, err, args)
    if code is None:
        print("""
poco.py Command [options]

Commands are:
   raw-pdf
       Show raw PDF chars.

   textual-pdf
       Show text PDF chars.
   textual-utf
       Show text as is (no strip of unicode/ UTF-8 chars)
   textual-latin
       My preferred show, ISO-8859-1 (Latin-1)

   seq-pdf
       Show PDF without excessive blanks
""")
        code = 0
    assert isinstance(code, int)
    assert code <= 127
    sys.exit(code)


def main_poco (outFile, errFile, args):
    """ Simple conversion script! """
    code = None
    debug = 0
    verbose = 0
    outName = None
    readKind = None
    if not args:
        return None
    cmd = args[0]
    param = args[1:]
    # Parse args
    while param and param[0].startswith( "-" ):
        if param[0].startswith( "-v" ):
            verbose += param[0].count( "v" )
            del param[ 0 ]
            continue
        if param[ 0 ].startswith( "-o" ):
            outName = param[1]
            del param[:2]
            continue
        print("Invalid option(s);\n", param)
        return None
    if verbose >= 3:
        print("Debug on!")
        debug = 1
    if outName is not None:
        outFile = open(outName, "wb")
    # Adjusts before run
    if cmd == "raw-pdf":
        readKind = "text"
    if cmd == "seq-pdf":
        readKind = "seq"    # no blanks
    elif cmd in ("textual-pdf",
                 "textual-latin",  # same as textual-pdf, but allowing Latin-1
                 "textual-utf",
                 ):
        readKind = "textual"
    # Command run
    inName = param[0]
    del param[0]
    if param:
        print("Extra parameter{}: {}"
              "".format("(s)" if len(param) > 1 else "", ", ".join(param)))
        return None
    if readKind is None:
        return None
    if cmd.find("latin") >= 0:
        readerControl.set_output_latin1()
    elif cmd.find("utf") >= 0:
        readerControl.set_output_utf8()
    code, cont = readerControl.pdf_text(inName, readKind, errFile, debug)
    if code:
        if code == 2:
            errFile.write("Cannot read pdf: {}\n".format(inName))
        else:
            errFile.write("No content: {}\n".format(inName))
    else:
        for line in cont:
            try:
                outFile.write("{}\n".format(line))
            except TypeError:
                outFile.write(bytes(line, "iso-8859-1"))
        code = 0
    if outName is not None:
        outFile.close()
    return code


def pre_strings(err):
    """ Minimal set of strings for test.
    """
    assert err is not None
    res = list()
    # Sample strings
    s_medio = "M\xc3\x89DIO"	# UTF-8 for 'MEDIO'
    #	U+00C9	E'	0xc3 0x89	LATIN CAPITAL LETTER E WITH ACUTE
    s_other = "Co\xe7a m\xe3o"		# Co&ccedil;a m&atilde;o
    for word in (s_medio, s_other,
                 ):
        a_word = []
        cont, _ = latinfy(word)
        for letra in cont:
            a_word.append(letra if ord(",") < ord(letra) <= 127 else hex(ord(letra)))
        s_word = ",".join(a_word)
        res.append(s_word)
    return res


#
# Main script
#
if __name__ == "__main__":
    main()
