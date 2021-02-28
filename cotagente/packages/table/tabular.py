# tabular.py  (c)2021  Henrique Moreira

"""
Simplest text tables
"""
# pylint: disable=missing-function-docstring, unused-argument

import table.stable as stable


class Tabular(stable.STableText):
    """ Tabular, 'simplest text' tables!
    """
    _refurbish_head = ""

    def __init__(self, fname=None, key_fields=None, split_chr=None, ref_str=""):
        self._remaining_fields = 0
        self._refurbish_head = ref_str
        if split_chr is None:
            self._splitter = self._default_splitter
        else:
            self._splitter = split_chr
        self._origin, self._rows = "", list()
        keys = key_fields if key_fields else tuple()
        if fname:
            self._add_from_file(fname)
            self._define_keys(keys, self.get_header())
        else:
            self._define_keys(keys, None)

    def get_header(self) -> tuple:
        """ get headline, should start with '#'.
        Same as STableKey!
        """
        head = self._rows[0]
        assert head[0] == "#"
        spl_chr = self._splitter
        return tuple(head[1:].strip().split(spl_chr))

    def _define_keys(self, keys: tuple, header) -> bool:
        """ Internal set of fields! """
        assert isinstance(keys, tuple)
        self._key_fields = keys
        self._all_fields = header
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
        return True

    def _add_from_file(self, fname) -> bool:
        self._origin, self._msg = fname, ""
        with open(fname, "r", encoding="ISO-8859-1") as f_in:
            data = f_in.read().splitlines()
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
    name = astr
    assert name
    pos = name.find("(")
    if pos > 0 and name.endswith(")"):
        name = name[:pos]
    assert name
    if name.endswith("*"):
        name = name[:-1]
        name.strip()
        assert name
        return 1, name
    return 0, name


# No main!
if __name__ == "__main__":
    print("Import, or see tests at tabular.test.py")
