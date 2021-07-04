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
    for name in sorted(vbx.props()):
        shown = vbx.props()[name]
        print(f"{name}: {shown}")
    return 0

def displayer(astr:str, nodes):
    # pylint: disable=unused-variable
    xtra = None
    print("displayer():", astr, "len:", len(nodes))
    for tup in nodes:
        if isinstance(tup, tuple):
            name, elem, attrib, text = tup
        else:
            print("alist:", tup)
            continue
        shown = xml_text(text)
        print(astr+":", name, f"text='{shown}',", f"attrib={elem.attrib}")
        print()


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

    def detag(self, tag:str):
        return tag.split('/')[-1].strip('}')

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
    elems = None
    _vm = None

    def __init__(self, path:str=""):
        super().__init__(path)
        self._process()

    @staticmethod
    def default_vm_dict() -> dict:
        vmd = {
            'HardDisks': list(),
            }
        return vmd

    def props(self) -> dict:
        """ Returns VM props dictionary. """
        assert self._vm
        return self._vm

    def _process(self) -> bool:
        self._vm = VBoxer.default_vm_dict()
        self.elems = list()
        if self._aroot is None:
            return False
        for one in self._aroot.iter():
            name = self.detag(one.tag)
            tup = (name, one, one.attrib, one.text)
            self.elems.append(tup)
        for tup in self.elems:
            name, elem, _, _ = tup
            if name not in self._vm:
                continue
            deep = [(self.detag(one.tag), one.attrib) for one in elem.iter()]
            print(":::", name, deep)
            self._vm[name] += deep
        return True

def xml_text(astr) -> str:
    """ Returns one line text display of a XML element text """
    if not astr:
        return ""
    return astr.strip().replace("\n", "^p")

# Main script
if __name__ == "__main__":
    print("Please import me.")
    main_test()
