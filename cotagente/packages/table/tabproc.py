# tabproc.py  (c)2021  Henrique Moreira

"""
Text table data processing
"""

# pylint: disable=no-self-use

from waxpage.redit import char_map


class HashedContent():
    """ HashedContent abstract class! """
    _key_join = "^"  # static
    _field_names = None

    def _recalculate_rows(self, data, first_num=1) -> dict:
        """ Returns dictionary indexed by (row) number. """
        adict, idx = dict(), first_num
        for row in data:
            adict[idx] = row
            idx += 1
        return adict

    def get_key_join_char(self) -> str:
        """ Return the char (or string) used to join several key values into a single string. """
        return self._key_join


class Content(HashedContent):
    """ Tabular (hashed) content
    """
    # pylint: disable=consider-using-enumerate

    _data = None

    def __init__(self, fields: tuple, header: str, payload=None, splitter: str=";"):
        """ Initialize Content() """
        self._data = None
        self._fields = fields
        self._header = tuple(header.split(splitter))
        self._payload = payload
        self._split_by = splitter
        assert isinstance(splitter, str)
        assert splitter
        self._field_names = tuple([name for name, _ in fields])

    def data(self) -> dict:
        """ Returns all data dictionary. """
        return self._data

    def raw_data(self) -> list:
        """ Return raw table lines. """
        return self._data["data"]

    def fields(self) -> tuple:
        """ Returns the tuple of fields, see Tabular().field_kinds()  """
        return self._fields

    def parse(self) -> bool:
        """ Returns if parse succeeded. """
        is_ok = self._parse_payload(self._payload)
        return is_ok

    def _parse_payload(self, payload):
        """ Parse text rows! """
        dkeys, single = dict(), dict()
        keying, fidx = list(), 0
        for _, key_idx in self._fields:
            if key_idx > 0:
                keying.append(fidx)
            fidx += 1
        all_data, errs = list(), list()
        idx = 0
        if not payload:
            return False
        for row in payload:
            idx += 1
            items = row.split(self._split_by)
            if len(items) != len(self._fields):
                msg = f"Invalid row#{idx}: field number mismatch: '{linear_text(row)}'"
                errs.append((msg, idx, row))
                continue
            values, fidx = list(), 0
            for fidx in range(len(items)):
                if fidx not in keying:
                    values.append(items[fidx])
            if keying:
                key_idx = keying[0] - 1
                if len(keying) == 1:
                    if items[key_idx] in single:
                        msg = f"Duplicate (single) key at row#{idx}: '{linear_text(row)}'"
                        errs.append((msg, idx, row))
                        continue
                    single[items[key_idx]] = tuple(values)
                else:
                    this_key = [items[col_idx] for col_idx in keying]
                    this_key = self._key_joiner().join(this_key)
                    if this_key in dkeys:
                        msg = f"Duplicate key at row#{idx}: '{linear_text(row)}'"
                        errs.append((msg, idx, row))
                        continue
                    dkeys[this_key] = tuple(values)
            all_data.append(items)
        if errs:
            self._data = {"errors": tuple(errs)}
            return False
        self._data = {
            "errors": tuple(),
            "data": all_data,
            "@single": single,
            "by-key": dkeys if dkeys else single,
            "by-idx": self._recalculate_rows(all_data),
        }
        return True

    def _keys_from_fields(self) -> list:
        """ Returns the list of keys """
        return [entry for entry, key_idx in self._fields if key_idx > 0]

    def __str__(self) -> str:
        """ Returns the list of fields """
        if self._data:
            return self._fields_list_str()
        return ""

    def _fields_list_str(self) -> str:
        """ Returns the list of fields """
        shown = repr(self._fields)
        s_keys = '+'.join(self._keys_from_fields())
        if s_keys:
            s_keys = f"keys: {s_keys}; "
        astr = f"{s_keys}str={shown}"
        return astr

    def _key_joiner(self) -> str:
        if self._key_join:
            return self._key_join
        assert self._split_by, "Expected a non-empty string to join key fields"
        return self._split_by


def linear_text(row: str) -> str:
    """ Returns escaped and simplified text. """
    if not row:
        return ""
    astr = row.replace("'", "\\'")
    return char_map.simpler_ascii(astr, 1)


# No main!
if __name__ == "__main__":
    print("Import table.tabproc !")
