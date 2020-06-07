# -*- coding: utf-8 -*-
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


class BaseCodeControl:
    """ Useful, and generic functions """
    def get_encoding(self):
        return sys.getdefaultencoding()

    def is_encoding_utf8(self):
        return self.get_encoding() == "utf-8"


class ReaderControl(BaseCodeControl):
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
        res, infos = latinfy(data)
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


def latinfy(a_str, n_line=0):
    """ Convert UTF-8 to ISO-8859-1, strict!
    """
    # cont = bytes(a_string, encoding="iso-8859-1")
    errs, fails = tuple(), 0
    if isinstance(a_str, str):
        data = to_bytes(a_str)
        # decode( ... , errors="strict")
        try:
            cont = data.decode("utf-8")
        except UnicodeDecodeError:
            fails += 1
    else:
        assert False
    if fails:
        lines = a_str.splitlines()
        cont, errs = latinfy_lines(lines)
    return cont, errs


def latinfy_lines(lines, debug=0):
    assert isinstance(lines, (list, tuple))
    res, errs = [], []
    idx_line = 0
    for line in lines:
        idx_line += 1
        data, fails = to_bytes(line), 0
        try:
            cont = data.decode("utf-8")
        except UnicodeDecodeError:
            fails += 1
        if fails:
            try:
                cont = data.decode("iso-8859-1")
            except UnicodeDecodeError:
                fails += 1
        if fails >= 2:
            plain = simpler_ascii(line)
            errs.append((plain, idx_line))
        else:
            plain = cont
        if debug > 0:
            show_infos([(plain, idx_line)], pre_text="fails={}, line=".format(fails))
        res.append(plain)
    return "\n".join(res), errs


def to_bytes(a_str):
    data = bytes([ord(x) for x in a_str])
    return data


def show_infos(infos, err=None, plain_data=True, pre_text="Error at line "):
    if err is None:
        err = sys.stderr
    for err_data, err_line in infos:
        what = err_data if plain_data else simpler_ascii(err_data)
        if err:
            err.write("{}{}: {}\n".format(pre_text, err_line, what))
    return len(infos) > 0


#
# Globals
#
readerControl = ReaderControl()


#
# Main script
#
if __name__ == "__main__":
    print("Import, or see tests at poco.test.py")
