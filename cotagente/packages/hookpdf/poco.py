# poco.py  (c)2019, 2020  Henrique Moreira

"""
  Dump pdf files in different ways.
"""

# pylint: disable=invalid-name, unused-argument, missing-function-docstring, no-self-use

# Hints:
#	see also basic: https://gist.github.com/serrasqueiro/62bf3ce8fcbd63433b75fb25b51addda

import sys
import PyPDF2
from hookpdf.pdfz import extractText
from waxpage.redit import char_map


def main():
    code = main_poco(sys.stdout, sys.stderr, sys.argv[ 1: ])
    if code is None:
        print("""
poco.py Command [options]

Commands are:
   raw-pdf
       Show raw PDF chars.

   textual-pdf
       Show text PDF chars.

   seq-pdf
       Show PDF without excessive blanks
""")
        code = 0
    assert isinstance(code, int)
    assert code <= 127
    sys.exit(code)


def main_poco (outFile, errFile, args):
    code = None
    debug = 0
    verbose = 0
    outName = None
    if not args:
        return None
    cmd = args[0]
    param = args[1:]
    # Parse args
    while param and param[ 0 ].startswith( "-" ):
        if param[ 0 ].startswith( "-v" ):
            verbose += param[ 0 ].count( "v" )
            del param[ 0 ]
            continue
        if param[ 0 ].startswith( "-o" ):
            outName = param[ 1 ]
            del param[ :2 ]
            continue
        print("Invalid option(s);\n", param)
        return None
    if verbose >= 3:
        print("Debug on!")
        debug = 1
    if outName is not None:
        outFile = open(outName, "w")
    # Adjusts before run
    readKind = "text"
    if cmd == "seq-pdf":
        readKind = "seq"    # no blanks
    elif cmd == "textual-pdf":
        readKind = "textual"
    # Command run
    if cmd in ("raw-pdf",
               "textual-pdf",
               "seq-pdf",
               ):
        inName = param[0]
        tup = readerControl.pdf_text( inName, readKind, errFile, debug )
        code, cont = tup
        if code:
            if code == 2:
                errFile.write("Cannot read pdf: {}\n".format( inName ))
            else:
                errFile.write("No content: {}\n".format(inName))
        else:
            for a in cont:
                outFile.write("{}\n".format(a))
        code = 0
    if outName is not None:
        outFile.close()
    return code


class ReaderControl:
    """ (PDF) reader control """
    def __init__ (self):
        self.initFuncOriginal = PyPDF2.pdf.PageObject.extractText
        self.excessiveStrsReplacement = (" ", ("\n", "\n(---)\n\n"))
        self.excCount = 0
        self.excMaxCount = 10**5


    def pdf_reader (self, aFile):
        """ Reader """
        fileReader = PyPDF2.PdfFileReader(aFile)
        return fileReader


    def pdf_text (self, inName, readKind="text", errFile=None, debug=0):
        """ PDF text """
        assert isinstance(inName, str)
        res = []
        isOriginal = readKind == "seq"
        isTextual = readKind == "textual"
        if isOriginal:
            PyPDF2.pdf.PageObject.extractText = self.initFuncOriginal
        else:
            PyPDF2.pdf.PageObject.extractText = extractText
        try:
            op = open(inName, "rb")
        except FileNotFoundError:
            op = None
        if op is None:
            return (2, res)
        pReader = self.pdf_reader(op)
        toASCII = "ASCII"
        cont = self.raw_content( pReader, toASCII )
        if cont is None:
            op.close()
            return (3, res)
        idx = 0
        for line in cont:
            idx += 1
            s = line.rstrip()
            if isTextual:
                readerControl.excCount = 0
                s = trim_excessive(s, self.excessiveStrsReplacement)
                if readerControl.excCount >= readerControl.excMaxCount:
                    if errFile is not None:
                        strShown = s.replace( "\n", "\\n" )
                        errFile.write("Excessive blanks ({}) in line {}, size {}: {:<.60}\n"
                                      "".format( readerControl.excCount, idx, len(s), strShown ))
            if debug > 0:
                print("Debug: #{} (type: {}, len={}, strip_len={})"
                      "".format( idx, type(line), len(line), len(s) ) )
                print(s, "<<<")
            res.append(s)
        op.close()
        return (0, res)


    def raw_content (self, pReader, altChr="?"):
        """ Dump raw content """
        toASCII = altChr == "ASCII"
        nPages = pReader.numPages
        res = []
        for pageNum in range(nPages):
            tuv = pReader.getPage(pageNum).extractText()
            assert isinstance(tuv, str)
            pageCont = ""
            last = ""
            for c in tuv:
                r = c
                if ord(c) == 0x2022:
                    r = "(o) "
                elif c == "~":
                    if last == c:
                        r = "\n"
                elif ord(c) >= 127:
                    if toASCII:
                        r = simpler_ascii(c)
                    elif altChr is not None:
                        r = altChr
                pageCont += r
                last = c
            res.append(pageCont)
        return res


def trim_excessive (s, chrs=(" ",), debug=0):
    assert isinstance(chrs, (tuple, list))
    for tup in chrs:
        sep = ""
        if isinstance(tup, tuple):
            e, sep = tup
            assert isinstance(sep, str)
        else:
            assert isinstance(tup, str)
            e = tup
        ee = e + e
        if sep == "":
            i = readerControl.excMaxCount
            while i > 0:
                last = s
                s = s.replace(ee, e)
                if s == last:
                    break
                readerControl.excCount += 1
                i -= 1
        else:
            idx = 9999
            while idx >= 0:
                idx -= 1
                pos1 = s.find(ee)
                pos2 = s.rfind(ee)
                if pos1 in (-1, pos2):
                    break
                s = s.replace(ee, e)
            if pos1 != -1:
                s = s.replace(ee, sep)
    return s


def simpler_ascii(a_chr):
    return char_map.simpler_ascii(a_chr)


#
# Globals
#
readerControl = ReaderControl()


#
# Main script
#
if __name__ == "__main__":
    main()
