# stable.py  (c)2020  Henrique Moreira

"""
Easy simple text tables
"""
# pylint: disable=missing-function-docstring, unused-argument, no-member

_ONLY_TXT_NL = True  # True: means, *no* CR in text files!


class STable():
    """ Simple Table """
    _origin = ""
    _rows = []
    _msg = ""

    def get_rows(self):
        return self._rows

    def get_msg(self):
        return self._msg

    def get_origin_file(self):
        return self._origin

    def _set_error(self, msg):
        if not msg:
            return False
        print(f"Error: {msg}")
        self._msg = msg
        return True


class STableText(STable):
    """ Text Table """
    _remaining_fields = 0

    def get_header(self) -> tuple:
        head = self._rows[0]
        assert head[0] == "#"
        spl_chr = self._splitter
        return tuple(head[1:].strip().split(spl_chr))

    def _add_from_file(self, fname) -> bool:
        self._origin = fname
        is_ok = True
        if _ONLY_TXT_NL:
            with open(fname, "rb") as f_temp:
                data = f_temp.read()
                if len(data) < 2:
                    return False
                is_ok = chr(data[-1]) == "\n" and chr(data[-2]) > ' '
                f_temp.close()
        with open(fname, "r", encoding="ISO-8859-1") as f_in:
            data = f_in.read().splitlines()
        for row in data:
            self._rows.append(row)
        self._msg = "" if is_ok else f"Bad-formatted-text: {fname}"
        return is_ok


class STableKey(STableText):
    """ Table with one key """
    _splitter = ";"
    _invalid_chrs_base = " :!?*()"
    _unique_k2 = True

    def __init__(self, fname=None, s_val_join=None, unique_k2=True):
        self._rows, self._msg = [], ""
        if fname:
            self._add_from_file(fname)
        self.keyval = (None, None, None)
        if s_val_join is None:
            self._s_val_join = ";"
        else:
            self._s_val_join = s_val_join
        self._remaining_fields = 0 if s_val_join else -1
        self._unique_k2 = unique_k2

    def hash_key(self, invalid_chrs=None, sort_as="A"):
        """ Hashes this table.
            sort_as='A' means order alphabetically, but ignore-case,
            sort_as='a' means order alphabetically (do not ignore case).
            sort_as='x' means no sort.
        """
        # pylint: disable=invalid-name
        inv_chars = self._get_basic_invalid(invalid_chrs)
        spl_chr = self._splitter
        key_to, from_name = dict(), dict()
        head = self._rows[0]
        rows = self._rows[1:]
        assert head.startswith("#")
        heads = head[1:].strip().split(spl_chr)
        idx = 1
        for row in rows:
            idx += 1
            assert row == row.strip()
            if self._remaining_fields == -1:
                pos = row.find(spl_chr)
                assert pos > 0
                cells = [row[:pos], row[pos+1:]]
            else:
                cells = row.split(spl_chr)
            if len(cells) != len(heads):
                xtra = "" if idx < len(self._rows) else " (last line)"
                srow = row if row else f"<empty-row>{xtra}"
                self._set_error(f"len(cells) {len(cells)} <> {len(heads)},"
                                f" line {idx}: {srow}")
                return False
            s_value = self._s_val_join.join(cells[1:])
            k1, k2 = cells[0], s_value
            assert k1 == k1.strip()
            assert k2 == k2.strip()
            if k1 in key_to:
                self._set_error(f"Duplicate key: {k1}")
                return False
            if inv_chars:
                for a_chr in k1:
                    if a_chr in inv_chars:
                        a_msg = f"Invalid key char, ASCII {ord(a_chr)}d = 0x{ord(a_chr):02x}: {k1}"
                        return not self._set_error(a_msg)
                    if a_chr < ' ' or a_chr > '~':
                        a_msg = f"Key char not ASCII7: {ord(a_chr)}d = 0x{ord(a_chr):02x}"
                        return not self._set_error(a_msg)
            key_to[k1] = k2
            if self._unique_k2 and k2 in from_name:
                self._set_error(f"Duplicate value: '{k2}'")
                return False
            from_name[k2] = k1
        ordered = list(key_to.keys())
        if sort_as == "A":
            ordered.sort(key=str.casefold)
        elif sort_as == "a":
            ordered.sort()
        else:
            assert sort_as == "x"
        self.keyval = (key_to, from_name, ordered)
        return True

    def _get_basic_invalid(self, invalid_chrs):
        if invalid_chrs is None:
            return ""
        if invalid_chrs == "@@":
            return self._invalid_chrs_base
        return invalid_chrs


#
if __name__ == "__main__":
    print("Import, or see tests at stable.test.py")
