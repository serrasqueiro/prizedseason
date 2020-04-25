#-*- coding: utf-8 -*-
# waxsize.py  (c)2020  Henrique Moreira

"""
European page sizes
"""

# pylint: disable=unused-argument

import sys

_DIMENSIONS = {"100ppi": ((850, 1168), (0.0, -1.0)),
               "200ppi": ((1700, 2338), (None, None)),
               }
_DIMENSION_A4 = ("200ppi", "100ppi",
                 )

_DIM_SIZE_A4 = (210.0, 297.0, "mm", "p")
_DIM_SIZE_A5 = (105.0, 148.0, "mm", "p")
_DIM_SIZE_A6 = (52.5, 74.0, "mm", "p")
_DIM_SIZE_A3 = (420.0, 594.0, "mm", "L")  # usual orientation ("L")

_PAGE_SIZES = {"A4": _DIM_SIZE_A4,
               "A5": _DIM_SIZE_A5,
               "A6": _DIM_SIZE_A6,
               "A3": _DIM_SIZE_A3,
               }

_PAGE_SIZE_METRIC = ("A4", "A5", "A6", "A3",
                     )


def main():
    """ Main basic tests! """
    def show_dims(dims):
        for d in dims:
            tup = _DIMENSIONS[d]
            s = shown_dim(tup, debug=1)
            print("{}: {}".format(d, s))
        return True

    def show_sizes(names, page_sizes):
        for name in names:
            width, height, unit, orient = page_sizes[name]
            s_orient = "Portrait" if orient == "p" else "Landscape" if orient == "L" else "?"
            s_extra = "{:.2f}".format(height / width)
            shown = "{}x{}{} (usually: {}) {}".format(width, height, unit, s_orient, s_extra)
            print("\t{}: {}".format(name, shown))
        return True

    args, code = sys.argv[1:], 0
    assert args == []
    dims = _DIMENSION_A4
    is_ok, used = verify_tups(_DIMENSIONS,
                              (_DIMENSION_A4,
                               ))
    if not is_ok:
        code = 1
        print("Bogus:", used)
    show_dims(dims)
    print("Page sizes (european):")
    show_sizes(_PAGE_SIZE_METRIC, _PAGE_SIZES)
    sys.exit(code)


def verify_tups(dct, dim_tups):
    """ Verify dimension dictionary and tuples. """
    assert isinstance(dct, dict)
    assert isinstance(dim_tups, (list, tuple))
    used = dict()
    is_ok, missing = True, []
    for k in dct.keys():
        used[k] = 0
    for tups in dim_tups:
        for tup in tups:
            if tup in used:
                used[tup] += 1
            else:
                missing.append(tup)
    if missing != []:
        return False, {"@": missing}
    for _, seen in used.items():
        if seen <= 0:
            is_ok = False
    return is_ok, used


def shown_dim(tup, debug=0):
    """ Basic dimension string """
    width, height = tup[0][0], tup[0][1]
    adj_x, adj_y = tup[1][0], tup[1][1]
    abs_x = width - (adj_x if adj_x is not None else 0)
    abs_y = height - (adj_y if adj_y is not None else 0)
    s_adj = "" if adj_y is None else "y{:.0f}pix".format(adj_y)
    s_ratio = "{:.2f}".format(abs_y / abs_x)
    s = "Width={}, Height={} ({}), ratio={}" \
        "".format(width, height, s_adj, s_ratio)
    assert (adj_x is None and adj_y is None) or \
           (isinstance(adj_x, float) and isinstance(adj_y, float))
    #print("abs_y:", abs_y)
    return s


# Main script
if __name__ == "__main__":
    main()
