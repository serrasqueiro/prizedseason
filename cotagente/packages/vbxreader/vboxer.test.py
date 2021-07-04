#!/usr/bin/python3
#-*- coding: ISO-8859-1 -*-
#
# vboxer.test.py  (c)2021  Henrique Moreira

"""
Tests vboxer.py
"""

# pylint: disable=missing-function-docstring

import sys
from vbxreader.vboxer import VBoxer, xml_text

def main():
    param = list()
    path = ""
    if len(sys.argv) > 1:
        path = sys.argv[1]
        param = sys.argv[2:]
    main_test(path, param)

def main_test(vbox_fname:str, param:list) -> int:
    """ Just testing """
    path = vbox_fname
    vbx = VBoxer(path)
    if not path:
        is_ok = vbx.process(sys.stdin.read())
        assert is_ok
    displayer("ALL", vbx.elems)
    for name in sorted(vbx.props()):
        shown = ""
        for item in vbx.props()[name]:
            shown += "\t" + f"{item}" + "\n"
        print(f"{name}:\n{shown}--\n")
    disks = vbx.by_area('hard-disk')
    print("Disks:", disks[0])
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


# Main script
if __name__ == "__main__":
    main()
