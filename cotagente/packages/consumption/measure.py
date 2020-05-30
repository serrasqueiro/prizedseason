# measure.py  (c)2020  Henrique Moreira

"""
  Measurement units and conversions
"""

# pylint: disable=unused-argument

from tconfig.adate import ShortDate, aDateMaster


class Formatter():
    _fmt_str = "{:0.0f}"	# or "{:0.3f}"

    def get_format_str(self):
        return self._fmt_str


class Measure(Formatter):
    """ Measurements... """
    measure = 0.0
    calendar = None
    _when, _week_day = "", ""
    new_format = None

    def __init__ (self, when=""):
        """ Initializer! """
        assert isinstance(when, str)
        self.measure = 0.0
        self.new_format = None
        self._set_when(when)


    def is_empty(self):
        return self._when == ""


    def __str__ (self):
        if self.new_format:
            fmt_str = self.new_format
        s = self._when + " " + self.get_format_str().format(self.measure)
        ###englishWeekday = aDateMaster.lang_week_day(self._week_day)
        ###s += ":::" + self.calendar.to_str() + "\t" + englishWeekday
        return s


    def _set_when(self, when):
        self._when, self._week_day = "", ""
        self.calendar = ShortDate()
        if not when:
            return False
        self.calendar.from_date(when)
        self._when = when
        self._week_day = aDateMaster.week_day(self.calendar)
        return True


#
# Test suite
#
if __name__ == "__main__":
    print("Import, or see tests at measure.test.py")
