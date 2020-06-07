# redit.py  (c)2020  Henrique Moreira

"""
  redit - Common functions to streams and files.

  Compatibility: python 3.
"""
# Replaces old 'redito' module.

# pylint: disable=missing-docstring, unused-argument, no-else-return, invalid-name
# pylint: disable=too-many-instance-attributes


import sys


_OTHER_LOOKUP_LIST = [
    (0xae,   "(R)", "&reg;", "Registered trademark", 0),
    (0xab,   "<<", "&laquo;", "Angle quotation mark (left)", 1),
    (0xbb,   ">>", "&raquo;", "Angle quotation mark (right)", 1),
    (0xa0,   " ", "&nbsp;", "Non-breaking space", 2),
    (0xb7,   "-", "&middot;", "Middle dot", 2),
    (0x2013, "--", "&ndash;", "EN dash", 2),
    (0x2014, "--", "&mdash;", "EM dash", 2),
    (0x201c, '"', "&ldquo;", "Left double quotation mark", 2),  # inverted open double-quotes
    (0x201d, '"', "&rdquo;", "Right double quotation mark", 2),  # inverted open double-quotes
    (0x0, "", "", "", -1)
    ]


class CharMap:
    """ CharMap class """
    subst, alt_subst = [], []
    otherLookup = []

    def __init__(self):
        self._init_charmap()

    def _init_charmap(self):
        self.subst = ['.'] * 256
        self.alt_subst = ['.'] * 256
        # Hint: for Unicode Character Map, e.g. UCS2 value 0x201c,
        #       see https://unicodemap.org/details/0x201c/index.html
        self.otherLookup = _OTHER_LOOKUP_LIST
        conv = ((0xc1, 'A', "A'"),  # A-acute
                (0xc9, 'E', "E'"),  # E-acute
                (0xcd, 'I', "I'"),  # I-acute
                (0xd3, 'O', "O'"),  # O-acute
                (0xda, 'U', "U'"),  # U-acute
                (0xe1, 'a', "a'"),  # a-acute
                (0xe9, 'e', "e'"),  # e-acute
                (0xed, 'i', "i'"),  # i-acute
                (0xf3, 'o', "o'"),  # o-acute
                (0xfa, 'u', "u'"),  # u-acute
                (0xc3, 'A', "A~"),  # A-tilde
                (0xd5, 'O', "O~"),  # O-tilde
                (0xe3, 'a', "a~"),  # a-tilde
                (0xf5, 'o', "o~"),  # o-tilde
                (0xc0, 'A', "'A"),  # A-grave
                (0xd4, 'O', "'O"),  # O-grave
                (0xe0, 'a', "'a"),  # a-grave
                (0xf4, 'o', "'o"),  # o-grave
                (0xc7, 'C', "C,"),  # C-cedil
                (0xe7, 'c', "c,"),  # c-cedil
                (0x0, '', ''))
        # Check if there are any repeated ASCII values
        idx = 0
        for tup in conv:
            assert len(tup) == 3
            asciiValue = tup[0]
            if asciiValue==0:
                break
            assert asciiValue >= 32
            for ch in conv[idx+1:]:
                assert asciiValue != ch[0]
            idx += 1
        idx = 0
        for tup in self.otherLookup:
            assert len(tup) == 5
            assert isinstance(tup[0], int)
            assert isinstance(tup[1], str)
            assert isinstance(tup[2], str)
            assert isinstance(tup[3], str)
            asciiValue = tup[0]
            if asciiValue == 0:
                break
            for ch in self.otherLookup[idx+1:]:
                assert asciiValue != ch[0]
            idx += 1
        # Start indexing:
        idx = 32
        while idx <= 255:
            if 32 <= idx < 127:
                chars = chr(idx)
                alt_chars = chars
            else:
                chars = "."
                alt_chars = chars
                for tup in conv:
                    val = tup[0]
                    if val == idx:
                        chars = tup[1]
                        alt_chars = tup[2]
                        break
            self.subst[idx] = chars
            self.alt_subst[idx] = alt_chars
            idx += 1
        for nc in ['\t', '\n']:
            self.subst[ord(nc)] = nc
            self.alt_subst[ord(nc)] = nc
        for nc in ['\r']:
            self.subst[ord(nc)] = ""
            self.alt_subst[ord(nc)] = ""
        return True


    def simpler_ascii(self, data, altText=0):
        s = ""
        if isinstance(data, str):
            for c in data:
                i = ord(c)
                if i >= 256:
                    chars = "?"
                else:
                    if altText == 0:
                        chars = self.subst[ i ]
                    else:
                        chars = self.alt_subst[ i ]
                s += chars
            return s
        elif isinstance(data, (list, tuple)):
            res = []
            for a in data:
                res.append(self.simpler_ascii(a, altText))
            return res
        elif isinstance(data, dict):
            res = []
            for k, val in data.items():
                s = self.simpler_ascii(val, altText)
                res.append((k, s))
            return res
        elif isinstance(data, (int, float)):
            s = data
        else:
            #print("simpler_ascii(): Unsupported type:", type( data ))
            assert False
        return s


    def find_other_lookup(self, asciiNum):
        assert isinstance(asciiNum, int)
        for tup in self.otherLookup:
            a = tup[ 0 ]
            if a == asciiNum:
                return tup
        return None


class BasicHistogram:
    """ Basic histogram class """
    seen = []

    def __init__(self, vMin=0, vMax=256):
        self.seen = []
        self.semiEmpty = []
        for _ in range(vMin, vMax+1):
            self.seen.append(0)


    def how_many(self, aChr):
        if isinstance(aChr, str):
            count = 0
            for c in aChr:
                count += self.seen[ord(c)]
        elif isinstance(aChr, int):
            count = self.seen[c]
        return count



class BinStream:
    """ BinStream abstract class """
    streamType = ""
    bomMarker = None

    def init_bin_stream(self):
        self.streamType = "UCS2"
        self.bomMarker = (0x0, 0x0)

    def set_textlike(self, shortString="TEXT"):
        assert isinstance(shortString, str)
        assert len(shortString)<10
        self.streamType = shortString

    def isLittleEndian(self):
        return self.bomMarker == (0xFF, 0xFE)

    def set_from_octets(self, bom0, bom1):
        if isinstance(bom0, str):
            return self.set_from_octets( ord(bom0), ord(bom1) )
        assert isinstance(bom0, int)
        assert isinstance(bom1, int)
        hasBOM = False
        if bom0 == 0xFF and bom1 == 0xFE:
            self.bomMarker = (0xFF, 0xFE)
            hasBOM = True
        return hasBOM



class TextRed(BinStream):
    """ TextRed abstract class """
    buf = ""
    _pname = ""

    def __init__(self, filename=""):
        self.init_bin_stream()
        self.numLines = 0
        self.numCR = 0  # usually we want to avoid '\r'
        self.byteSize = 0
        self.noEOL = False
        self.clutterChrs = []
        self.nonASCII7 = []
        self.skipNonASCII7bit = True
        self.convertToLatin1 = False
        self.nonASCII7Str = "."
        self.lines = []
        self.extension = ( "", [""] )
        self.set_filename( filename )
        self.histogram = BasicHistogram()
        self.inEncoding = "ascii"
        self.top_init()


    def get_filename(self):
        return self._pname


    def set_filename(self, filename):
        if filename:
            self._pname = filename
        else:
            self._pname = ""
        pos = filename.rfind( "." )
        coName = ""
        if pos > 0:
            ext = filename[pos:]
        else:
            ext = ""
        uExt = ext.lower()
        if ext == '.py':
            coName = "PYTHON"
        elif uExt == '.pdf':
            coName = "PS"  # postscript
        self.extension = ( ext, [coName] )
        return coName


    def file_coname(self):
        return self.extension[ 1 ][ 0 ]


    def extension_matches(self, aStr):
        aExt = self.extension[1]
        assert len(aExt) == 1
        assert isinstance(aExt, list)
        assert isinstance(aStr, str)
        return aExt[0] == aStr


    def utf_file_reader(self, filename=None):
        self.inEncoding = "utf-8"
        self.convertToLatin1 = True
        isOk = self.file_reader( filename )
        return isOk


    def file_reader(self, filename=None):
        f = None
        if filename:
            inName = filename
            self._pname = inName
        else:
            inName = self._pname
        isOk = True
        try:
            f = open(inName, "rb")
        except FileNotFoundError:
            isOk = False
        self.buf = ""
        if isOk:
            f.close()
            if self.inEncoding == "ascii":
                f = open(inName, "rb")
            else:
                f = open(inName, "r", encoding=self.inEncoding)
            self.buf = f.read()
            f.close()
        else:
            isOk = inName == ""
            if isOk:
                sys.stdin = sys.stdin.detach()
                f = sys.stdin
                self.set_textlike()
                self.buf = f.read()
        if f:
            if isinstance(self.buf, bytes):
                #mayHaveBOM = len(self.buf) >= 2
                hasBOM = self.set_from_octets( self.buf[ 0 ], self.buf[ 1 ] )
            else:
                hasBOM = False
            if hasBOM:
                self.add_content(self.buf[ 2: ], 2)
            else:
                self.set_textlike()
                self.add_content(self.buf, 1)
        return isOk


    def add_content(self, data, ucs=1):
        if ucs == 2:
            return self._add_ucs_content(data)
        return self._add_normal_content(data)


    def add_lines(self, lines):
        assert isinstance(lines, str)
        listed = lines.splitlines()
        for line in listed:
            self.numLines += 1
            self.lines.append(line)
            if len(line) > 0 and len(line.strip()) == 0:
                self.histogram.semiEmpty.append(self.numLines)
        return len(listed)


    def is_text_ok(self, requireASCII7=True):
        dosLike = self.numLines == self.numCR
        isOk = (dosLike or self.numCR == 0) and len( self.clutterChrs ) == 0
        if requireASCII7 and len( self.nonASCII7 ) > 0:
            isOk = False
        return isOk


    def _add_ucs_content(self, data):
        self.byteSize += len(data)
        isOk = False
        isLittle = self.isLittleEndian()
        coil = []
        idx = 0
        lineNr = -1
        if isLittle:
            for p in data:
                even = (idx % 2) == 0
                if isinstance(p, int):
                    val = p
                else:
                    val = ord(p)
                assert isinstance(val, int)
                if even:
                    coil.append(val)
                else:
                    if val > 0:
                        self.histogram.seen[256] += 1
                        self.nonASCII7.append( (lineNr, idx, format(val, "#02x")) )
                idx += 1
                isOk = self.add_content(coil, 1)
        return isOk

    def _add_normal_content(self, data):
        self.byteSize += len(data)
        s, col = "", 0
        for el in data:
            if isinstance(el, str):
                c = ord(el)
            else:
                c = el
            nonISO_tup = None
            if c < len(self.histogram.seen):
                self.histogram.seen[c] += 1
            if c == ord('\n'):
                self.add_lines(s)
                s = ""
                col = 0
            elif c == ord('\r'):
                self.numCR += 1
            elif c < ord(' ') and c != ord('\r') and c != ord('\t'):
                self.clutterChrs.append( (self.numLines+1, 0, format(c, "#02x")) )
                s += "?"
            else:
                col += 1
                if c<127 or not self.skipNonASCII7bit:
                    s += chr( c )
                else:
                    if self.convertToLatin1 and c<256:
                        conv = char_map.simpler_ascii(chr(c))
                        if c >= 127 and conv == '.':
                            other = char_map.find_other_lookup(c)
                            if other:
                                conv = other[1]
                            else:
                                nonISO_tup = (self.numLines+1, col, format(c, "#02x")+" .")
                        s += conv
                    else:
                        other = char_map.find_other_lookup( c )
                        if other:
                            chup = other[1]
                        else:
                            chup = self.nonASCII7Str
                            nonISO_tup = (self.numLines+1, col, format(c, "#02x"))
                        s += chup
            if nonISO_tup:
                self.nonASCII7.append(nonISO_tup)
        if s:
            self.noEOL = True
            self.add_lines(s+"\n")
        return True


class BareText(TextRed):
    """ BareText class """

    userDefined = []

    def top_init(self):
        self.userDefined = []

    def __str__(self):
        return self.to_str()

    def to_str(self):
        return self.info()

    def info(self):
        txt = self.text_platform()
        sProp2 = txt + ";" + self.inEncoding + ";" + "nonASCII=" + str(len(self.nonASCII7))
        sProp = f"lines={len(self.lines)};" + \
                f"{self.extension[0]}:{self.extension[1]};" + \
                f"{sProp2}"
        s = self._pname + "\n" + sProp
        return s

    def text_platform(self):
        txt = "DOS_CR" if self.numCR == len(self.lines) or (self.numCR > 0 and self.noEOL) else \
              "NL" if self.numCR == 0 else "MixCR"
        return txt


class WildStr:
    """ Wild-card string """
    s = ""
    wild = ""
    left, middle, right = "", "", ""

    def __init__(self, aStr, wildCard="@@"):
        assert isinstance(aStr, str)
        self.s = ""
        self.wild = wildCard
        self.left = ""
        self.middle = ""
        self.right = ""
        self.init_wild_str( aStr, [self.wild] )

    def clear(self):
        self.s = ""
        self.left = ""
        self.middle = ""
        self.right = ""

    def init_wild_str(self, aStr, wildList):
        assert isinstance(aStr, str)
        for w in wildList:
            if len(w) <= 0:
                assert isinstance(w, str)
                self.s = aStr
                return False
            spl = aStr.split(w)
            if len(spl) == 2:
                self.left = spl[0]
                self.right = spl[1]
                self.middle = ""
            else:
                self.s = aStr
        return True

    def by_name(self, aName):
        if not self.s:
            self.middle = aName
            self.s = self.left + self.middle + self.right
        return self.s

    def by_pathname(self, aName):
        if not self.s:
            pos = any_chr_rev(aName, ['/', '\\'])
            if pos >= 0:
                self.middle = aName[pos+1:]
            else:
                self.middle = aName
            self.s = self.left + self.middle + self.right
        return self.s


def any_chr_rev(aStr, anyChr):
    """ Any character find, backwards (reverse) """
    idx = len(aStr)
    while idx > 0:
        idx -= 1
        c = aStr[idx]
        assert isinstance(c, str)
        found = c in anyChr
        if found:
            return idx
    return -1


#
# Global
#
char_map = CharMap()


#
# Test suite
#
if __name__ == "__main__":
    print("Import, or see tests at redit.test.py")
