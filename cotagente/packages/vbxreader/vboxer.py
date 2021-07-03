#-*- coding: ISO-8859-1 -*-
# vboxer.py  (c)2021  Henrique Moreira

"""
VirtualBox vbox text-file reader
"""

# pylint: disable=missing-function-docstring

from lxml import etree


class GenXML():
    """ Generic XML reader """
    # pylint: disable=no-self-use

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

    def all_props(self) -> dict:
        """ Returns all VM props dictionary. """
        assert self._vm
        return self._vm

    def props(self) -> dict:
        """ Returns only the VM props dictionary. """
        assert self._vm
        return self._vm['VM']

    def by_area(self, key:str):
        result = self._vm['area'].get(key)
        if not result:
            return list()
        return result

    @staticmethod
    def default_vm_dict() -> dict:
        vmd = {
            'VM': {
                'HardDisks': list(),
            },
            'area': {
                'hard-disk': list(),
            },
        }
        return vmd

    def process(self, data:str) -> bool:
        self._reader(data)
        return self._process()

    def _process(self) -> bool:
        vmd = VBoxer.default_vm_dict()
        self._vm = vmd
        self.elems = list()
        if self._aroot is None:
            return False
        for one in self._aroot.iter():
            name = self.detag(one.tag)
            tup = (name, one, one.attrib, one.text)
            self.elems.append(tup)
        for tup in self.elems:
            name, elem, _, _ = tup
            if name not in self.props():
                continue
            els = elem.getchildren()
            deep = [(self.detag(one.tag), one.attrib) for one in els]
            self._vm['VM'][name] += deep
        self._simplify(self._vm['area'])
        return True

    def _simplify(self, dest):
        atypes = ("Normal",)
        els = [attr for name, attr in self.props()['HardDisks'] if name == "HardDisk"]
        dest['hard-disk'] = [
            [item['location'] for item in els if item['type'] in atypes]
        ]

def xml_text(astr) -> str:
    """ Returns one line text display of a XML element text """
    if not astr:
        return ""
    return astr.strip().replace("\n", "^p")

# Main script
if __name__ == "__main__":
    print("Please import me.")
