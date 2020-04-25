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


def main():
    """ Main basic tests! """
    def show_dims(dims):
        for d in dims:
            tup = _DIMENSIONS[d]
            s = shown_dim(tup, debug=1)
            print("{}: {}".format(d, s))
        return True

    args, code = sys.argv[1:], 0
    assert args == []
    dims = _DIMENSION_A4
    show_dims(dims)
    sys.exit(code)


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
