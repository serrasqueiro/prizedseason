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


_EXCESSIVE_BLANKS_MAX_COUNT = 10**5


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
        outFile = open(outName, "w")
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
    tup = readerControl.pdf_text(inName, readKind, errFile, debug)
    code, cont = tup
    if code:
        if code == 2:
            errFile.write("Cannot read pdf: {}\n".format(inName))
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
    _initFuncOriginal = None
    excCount = 0
    _excMaxCount = _EXCESSIVE_BLANKS_MAX_COUNT
    _content_coding = "ASCII"
    #_histogram = (256+1) * [0]

    def __init__ (self, content_coding=None):
        self._initFuncOriginal = PyPDF2.pdf.PageObject.extractText
        self.excessiveStrsReplacement = (" ", ("\n", "\n(---)\n\n"))
        self.excCount = 0
        if content_coding is not None:
            assert content_coding
            self._content_coding = content_coding


    def set_output_ascii(self):
        self._content_coding = "ASCII"

    def set_output_latin1(self):
        self._content_coding = "ISO-8859-1"

    def set_output_utf8(self):
        self._content_coding = "UTF-8"


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
            PyPDF2.pdf.PageObject.extractText = self._initFuncOriginal
        else:
            PyPDF2.pdf.PageObject.extractText = extractText
        try:
            op = open(inName, "rb")
        except FileNotFoundError:
            op = None
        if op is None:
            return (2, res)
        pReader = self.pdf_reader(op)
        cont = self.raw_content(pReader)
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
                if readerControl.excCount >= readerControl.excessive_max_count():
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
        res = self._readable_content(pReader, self._content_coding, altChr)
        return res


    def _readable_content(self, pReader, coding, altChr):
        res = []
        toASCII =  coding == "ASCII"
        latin1 = coding == "ISO-8859-1"
        utf = coding == "UTF-8"
        if utf:
            altChr = None
        nPages = pReader.numPages
        for pageNum in range(nPages):
            tuv = pReader.getPage(pageNum).extractText()
            assert isinstance(tuv, str)
            pageCont = ""
            last = ""
            rats = 0
            for c in hack_str(tuv):
                code = ord(c)
                r = c
                if c == "~":
                    if last == c:
                        r = "\n"
                elif code >= 127:
                    if toASCII:
                        r = simpler_ascii(c)
                    elif latin1:
                        rats += 1
                    elif altChr is not None:
                        r = altChr
                pageCont += r
                last = c
            if rats:
                pageCont, _ = self._from_utf(pageCont, rats)
            res.append(pageCont)
        return res


    def excessive_max_count(self):
        return self._excMaxCount


    def _from_utf(self, data, rats):
        """ Tries to convert string 'data' into valid ISO-8859-1 (latin-1) """
        assert isinstance(data, str)
        infos = tuple()
        res = data
        return res, infos


def trim_excessive (s, chrs=(" ",), debug=0):
    """ Trim excessive blanks """
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
            i = readerControl.excessive_max_count()
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


def hack_str(a_str):
    res = a_str.replace(chr(0x2022), "(o) ")
    return res


#
# Globals
#
readerControl = ReaderControl()


#
# Main script
#
if __name__ == "__main__":
    main()
