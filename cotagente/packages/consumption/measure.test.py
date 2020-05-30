# measure_test.py  (c)2020  Henrique Moreira

"""
  Test for measure.py
"""

# pylint: disable=unused-argument


import sys
from consumption.measure import Measure


def main():
    """ Main test script! """
    prog = __file__
    code = test_measure(sys.stdout, sys.stderr, sys.argv[1:])
    if code is None:
        print(f"""Usage:

{prog}
""")
        code = 0
    assert code == 0
    sys.exit(code)


def test_measure(out, err, args):
    """ Main module test! """
    tests = ("", "2020-05-30",)
    for dat in tests:
        meas = Measure(dat)
        val = 100.0
        meas.measure = val
        print("meas '{}', empty? {}: {}".format(dat, meas.is_empty(), meas))
        is_ok = (meas.is_empty() and dat == "") or (not meas.is_empty() and dat)
        assert is_ok
    return 0


#
# Test suite
#
if __name__ == "__main__":
    main()
