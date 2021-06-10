# tabular.py  (c)2021  Henrique Moreira

"""
Simplest text tables
"""
# pylint: disable=missing-function-docstring, unused-argument, too-many-instance-attributes

import table.stable as stable
import table.tabproc as tabproc


class Tabular(stable.STableText):
    """ Tabular, 'simplest text' tables!
    """
    _refurbish_head = ""

    def __init__(self, fname=None, data:str="", key_fields=None, split_chr=None, ref_str=""):
        self._remaining_fields = 0
        self._refurbish_head = ref_str
        if split_chr is None:
            self._splitter = self._default_splitter
        else:
            self._splitter = split_chr
        self._origin, self._rows = "", list()
        keys = key_fields if key_fields else tuple()
        if fname:
            assert data == ""
            self._add_from_file(fname)
            self._define_keys(keys, self.get_header())
        else:
            assert fname is None, "Either 'fname' or 'data'"
            self._add_from_data(data)
            self._define_keys(keys, self.get_header())
        assert self._fields is not None
        assert isinstance(self._fields, tuple)
        if self._fields:
            header = self._rows[0]
            self._content = tabproc.Content(self._fields, header, self._rows[1:], self._splitter)
        else:
            self._content = tabproc.Content(tuple(), "")

    def get_header(self) -> tuple:
        """ get headline, should start with '#'.
        Same as STableKey!
        """
        head = self._rows[0]
        assert head[0] == "#"
        spl_chr = self._splitter
        return tuple(head[1:].strip().split(spl_chr))

    def split_by(self) -> str:
        """ Returns _splitter string (char) """
        return self._splitter

    def keys(self) -> tuple:
        """ Returns a tuple of strings with key fields. """
        return self._key_fields

    def field_kinds(self) -> tuple:
        """ Returns tuple of pairs (field_name, n) for all fields.
         0 are non-keys, 1..n are the keys.
         """
        return self._fields

    def content(self):
        """ Return the table payload content. """
        return self._content

    def _define_keys(self, keys:tuple, header) -> bool:
        """ Internal set of fields! """
        assert isinstance(keys, tuple)
        self._key_fields = keys
        self._all_fields = header
        self._fields = tuple()
        if not header:
            return True
        assert isinstance(header, tuple)
        # Interpret header tuple:
        #	'a_field*' means a key
        #	'b_expr(bool)' means field 'b_expr' is a boolean
        k_there = [key_field_str(elem) for elem in header if is_key_field(elem)]
        if keys:
            # Check if requested keys are all there:
            if keys != tuple(k_there):
                self._msg = f"define_keys {keys} mismatch: {k_there}"
                return False
        self._key_fields = keys
        self._all_fields = tuple([key_field_str(elem) for elem in header])
        fields_kind, key_idx = list(), 0
        for name in self._all_fields:
            if name in self._key_fields:
                key_idx += 1
                tup = (name, key_idx)
            else:
                tup = (name, 0)
            fields_kind.append(tup)
        self._fields = tuple(fields_kind)
        return True

    def _add_from_file(self, fname) -> bool:
        self._origin = fname
        with open(fname, "r", encoding="ISO-8859-1") as f_in:
            content = f_in.read()
        return self._add_from_data(content)

    def _add_from_data(self, content:str) -> bool:
        self._msg = ""
        data = content.splitlines()
        if not data:
            return False
        if data[0].startswith("#"):
            if self._refurbish_head:
                data = self._refurbish_head.split("\n") + data[1:]
        for row in data:
            self._rows.append(row)
        return True


def is_key_field(astr) -> bool:
    """ Returns True if string looks a key string.
    """
    return _key_field(astr)[0]

def key_field_str(astr) -> str:
    """ Returns the string of a key field
    """
    return _key_field(astr)[1]

def _key_field(astr) -> tuple:
    """ Returns (int, name) -> whether field looks like a key, and its name.
    """
    name = astr.strip()
    is_key = name.endswith("*")
    if is_key:
        name = name[:-1].rstrip()
    assert name
    pos = name.find("(")
    if pos > 0 and name.endswith(")"):
        name = name[:pos]
    assert name
    return int(is_key), name


# No main!
if __name__ == "__main__":
    print("Import, or see tests at tabular.test.py")
