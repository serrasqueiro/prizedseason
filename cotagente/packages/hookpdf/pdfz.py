# -*- coding: utf-8 -*-
# pdfz.py  (c)2019, 2020  Henrique Moreira (part of 'hookpdf')

"""
  Extension to PyPDF2

  Compatibility: python 3.
"""

# pylint: disable=invalid-name, unused-argument, missing-function-docstring

import sys
#import PyPDF2.pdf as updf
from PyPDF2.pdf import \
     ContentStream, \
     TextStringObject, \
     b_
from PyPDF2.utils import u_


def main():
    """ Basic tests, if needed. """
    args = sys.argv[1:]
    code = test_pdfz(sys.stdout, sys.stderr, args)
    assert isinstance(code, int)
    sys.exit(code)


def test_pdfz (outFile, errFile, args):
    """ Nothing currently! """
    assert args == []
    return 0


def extractText (obj, which_one="alt"):
    """
    Locate all text drawing commands, in the order they are provided in the
    content stream, and extract the text.  This works well for some PDF
    files, but poorly for others, depending on the generator used.  This will
    be refined in the future.  Do not rely on the order of text coming out of
    this function, as it will change if this function is made more
    sophisticated.

    :return: a unicode string object.
    """
    def original_extractText (self):
        text = u_("")
        content = self["/Contents"].getObject()
        if not isinstance(content, ContentStream):
            content = ContentStream(content, self.pdf)
        # Note: we check all strings are TextStringObjects.  ByteStringObjects
        # are strings where the byte->string encoding was unknown, so adding
        # them to the text here would be gibberish.
        for operands, operator in content.operations:
            if operator == b_("Tj"):
                _text = operands[0]
                if isinstance(_text, TextStringObject):
                    text += _text
            elif operator == b_("T*"):
                text += "\n"
            elif operator == b_("'"):
                text += "\n"
                _text = operands[0]
                if isinstance(_text, TextStringObject):
                    text += operands[0]
            elif operator == b_('"'):
                _text = operands[2]
                if isinstance(_text, TextStringObject):
                    text += "\n"
                    text += _text
            elif operator == b_("TJ"):
                for i in operands[0]:
                    if isinstance(i, TextStringObject):
                        text += i
                text += "\n"
        return text


    def alt_extractText (self):
        """
        Locate text and include "\n"

        :return: a unicode string object.
        """
        pic = ""
        tic = "~"
        text = u_("")
        content = self["/Contents"].getObject()
        if not isinstance(content, ContentStream):
            content = ContentStream(content, self.pdf)
        for operands, operator in content.operations:
            if operator == b_("Tj"):
                _text = operands[0]
                if isinstance(_text, TextStringObject):
                    text += _text + pic
            elif operator == b_("T*"):
                text += "\n"
            elif operator == b_("'"):
                text += "\n"
                _text = operands[0]
                if isinstance(_text, TextStringObject):
                    text += operands[0]
            elif operator == b_('"'):
                _text = operands[2]
                if isinstance(_text, TextStringObject):
                    text += "\n"
                    text += _text
            elif operator == b_("TJ"):
                for i in operands[0]:
                    if isinstance(i, TextStringObject):
                        text += i
                text += "\n"
            else:
                text += tic
        return text


    if which_one == "original":
        text = original_extractText(obj)
    elif which_one == "alt":
        text = alt_extractText(obj)
    else:
        assert False
    return text


if __name__ == "__main__":
    main()
