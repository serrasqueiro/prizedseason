# bdate.py  (c)2019  Henrique Moreira (part of 'horaconta')

"""
  Basic date handling (pt)

  Compatibility: python 2 and 3.
"""

import datetime


#
# CLASS BDate
#
class BDate:
  def __init__ (self, val=0):
    self.set_invalid()
    if type( val )==int:
      pass
    elif type( val )==str:
      self.set_bdate( val )
    else:
      assert False
    pass


  def set_invalid (self):
    self.ymd = (0, 0, 0)
    self.asValue = 0
    self.asStr = "-"


  def __str__ (self):
    return self.asStr


  def set_bdate (self, val):
    iVal = None
    if type( val )==str:
      """
	# datetime_str = '09/30/18 13:55:26'
	# datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')
      """
      if len( val )==8:
        iVal = int( val )
        assert iVal>=2000*100*100
      elif len( val )==10:
        dt = datetime.datetime.strptime(val, "%d-%m-%Y")
      else:
        assert False
    else:
      assert False
    if iVal is None:
      year = dt.year
      month = dt.month
      day = dt.day
      iVal = year
      iVal *= 100
      iVal += dt.month
      iVal *= 100
      iVal += dt.day
    else:
      v = iVal
      day = v % 100
      v //= 100
      month = v % 100
      v //= 100
      year = v
    self.ymd = (year, month, day)
    self.asValue = iVal
    self.calc_str()
    return iVal


  def calc_str (self, format=None):
    self.asStr = self.date_as_str( self.ymd[0], self.ymd[1], self.ymd[2], format )


  def date_as_str (self, year, month, day, format=None):
    dt = datetime.datetime( year, month, day )
    if format is not None:
      assert type( format )==str
    else:
      format = "%d-%m-%Y"
    return dt.strftime( format )


  def diff (self, d, incr=0):
    # d is the other BDate
    dt1 = datetime.datetime( self.ymd[0], self.ymd[1], self.ymd[2] )
    dt0 = datetime.datetime( d.ymd[0], d.ymd[1], d.ymd[2] )
    dtDiff = dt1-dt0
    days = dtDiff.days
    return days+incr


#
# basic_ascii_tree()
#
def basic_ascii_tree (binInfo):
  lines = binInfo.decode("ascii").replace("\t", "  ").split("\n")
  return lines


#
# simpler_str()
#
def simpler_str (s):
  while True:
    r = s.strip().replace( "  ", " " )
    if r==s:
      return r
    s = r
  pass

