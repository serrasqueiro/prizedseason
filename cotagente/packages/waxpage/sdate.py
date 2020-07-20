# sdate.py  (c)2020  Henrique Moreira

"""
  sdate - Easy hard-coded functions to convert dates

  Compatibility: python 3.
"""
# pylint: disable=unused-argument

import sys
import datetime

def from_abbrev_date(date_string) -> datetime.datetime:
    """ Converts string to datetime object. """
    return datetime.datetime.strptime(date_string, "%d.%m.%Y")

def date_to_string(dttm) -> str:
    return dttm.strftime("%d.%m.%Y")

#
# Test suite
#
if __name__ == "__main__":
    print("Import, or see tests at sdate.test.py")
