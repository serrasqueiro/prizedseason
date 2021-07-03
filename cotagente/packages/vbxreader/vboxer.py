#-*- coding: ISO-8859-1 -*-
# vboxer.py  (c)2021  Henrique Moreira

"""
VirtualBox vbox text-file reader
"""

# pylint: disable=missing-function-docstring

import sys
from lxml import etree

def main_test() -> int:
    """ Just testing """
    path = sys.argv[1]
    vbx = VBoxer(path)
    displayer("ALL", vbx.elems)
    return 0

def displayer(astr:str, nodes):
    xtra = None
    for tup in nodes:
        if isinstance(tup, tuple):
            name, elem = tup
        else:
            displayer("ITEM", [one for one in tup])
            continue
        print(astr+":", name, elem)
        if name == "ExtraData":
            xtra = elem
        print()
    if xtra is not None:
        displayer("EXTRA", xtra)


class GenXML():
    """ Generic XML reader """
    _enc_read = "ISO-8859-1"	# static!
    _path = ""
    _data = ""
    _aroot = None

    def __init__(self, path:str=""):
        """ Initializer """
        self._path, self._data = path, ""
        self._aroot = None
        enc = self._enc_read if self._enc_read else "ascii"
        if path:
            self._reader(open(path, "r", encoding=enc).read())

    def root(self):
        """ Returns the xml root """
        assert self._aroot is not None
        return self._aroot

    def _reader(self, data:str):
        self._data = data
        cont = data
        if "encoding=" in cont.splitlines()[0]:
            lines = ['<?xml version="1.0"?>'] + cont.splitlines()[1:]
            cont = '\n'.join(lines)
        self._set_from_data(cont)

    def _set_from_data(self, data:str):
        root = etree.fromstring(data)
        self._aroot = root
        return root

class VBoxer(GenXML):
    """ vbox (VirtualBox) text-file reader """
    def __init__(self, path:str=""):
        super().__init__(path)
        self._process()

    def _process(self) -> bool:
        if self._aroot is None:
            return False
        els = self.root()[0]
        self.elems = [(one.tag.split('/')[-1].strip('}'), one) for one in els]
        return True

# Main script
if __name__ == "__main__":
    print("Please import me.")
    main_test()
