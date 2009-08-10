'''Date parsing and normalization utilities based on FlexiDate.

FlexiDate is focused on supporting:

  1. Dates outside of Python (or DB) supported period (esp. dates < 0 AD)
  2. Imprecise dates (c.1860, 18??, fl. 1534, etc)
  3. Normalization of dates to machine processable versions
  4. Sortable in the database (in correct date order)
  5. Human readability as dates will be re-edited/viewed by people
    * As we know best this = preservation of "user" entered dates 

Not all of these requirements are satisfiable at once in a simple way.

Be clear about what we want:

  1. Storage (and preservation) of "user" dates (both normal and non-normal)
  2. Normalization of dates (e.g. to ~ ISO 8601)
  3. Integration with database (sortability and serializability)

Solution for 1: Represent dates as strings.

Solution for 2: Have a parser (via an intermediate FlexiDate object).

Solution for 3:
===============

Remark: no string based date format will sort dates correctly based on std
string ordering (PF: let x,y be +ve dates and X,Y their string representations
then if X<Y => -X<-Y (wrong!))

Thus we need to add some other field if we wish dates to be correctly sorted
(or not worry about sorting of -ve dates ...)

1. For any given date attribute have 2 actual fields:

  * user version -- the version edited by users
  * normalized/parsed version -- a version that is usable by machines

2. Store both versions in a single field but with some form of serialization.

3. Convert dates to long ints (unlimited in precision) and put this in a
separate field and use that for sorting.


Comments
++++++++

Initially thought that we should parse before saving into a FlexiDate format
but: a) why bother b) when parsing always hard not to be lossy (in particular
when converting to iso8601 using e.g. dateutil very difficult to not add info
e.g. parsing 1860 can easily give us 1860-01-01 ...).


Existing Libraries
++++++++++++++++++

See: http://wiki.python.org/moin/WorkingWithTime

ISO 8601: [3]


References
==========

[1]: http://www.feedparser.org/docs/date-parsing.html
[2]: http://seehuhn.de/pages/pdate
[3]: http://code.google.com/p/pyiso8601/source/browse/trunk/iso8601/iso8601.py
'''
import re
import datetime

class FlexiDate(object):
    """Store dates as strings and present them in a slightly extended version
    of ISO8601.

    Modifications:
        * Allow a trailing qualifiers e.g. fl.
        * Allow replacement of unknown values by ? e.g. if sometime in 1800s
          can do 18??
    
    Restriction on ISO8601:
        * Truncation (e.g. of centuries) is *not* permitted.
        * No week and day representation e.g. 1999-W01
    """
    # pass
    def __init__(self, year=None, month=None, day=None, qualifier=''):
        # force = month or day or qualifier
        force = False
        self.year = self._cvt(year, rjust=4, force=force)
        self.month = self._cvt(month)
        self.day = self._cvt(day)
        self.qualifier = qualifier
         
    def _cvt(self, val, rjust=2, force=False):
        if val:
            tmp = unicode(val).strip()
            if tmp.startswith('-'):
                tmp = '-' + tmp[1:].rjust(rjust, '0')
            else:
                tmp = tmp.rjust(rjust, '0')
            return tmp
        elif force:
            # use '!' rather than '?' as '!' < '1' while '?' > '1'
            return rjust * '!'
        else:
            return ''

    def __str__(self):
        out = self.isoformat()
        if self.qualifier:
            # leading space is important as ensures when no year sort in right
            # order as ' ' < '1'
            out += u' [%s]' % self.qualifier
        return out

    def __repr__(self):
        return u'%s %s' % (self.__class__, self.__str__())

    def isoformat(self, strict=False):
        '''Return date in isoformat (same as __str__ but without qualifier).
        
        WARNING: does not replace '?' in dates unless strict=True.
        '''
        out = self.year
        # what do we do when no year ...
        for val in [ self.month, self.day ]:
            if not val:
                break
            out += u'-' + val
        if strict:
            out = out.replace('?', '0')
        return out

    our_re_pat = '''
        (?P<year> -?[\d?]+)
        (?:
                \s* - (?P<month> [\d?]{1,2})
            (?: \s* - (?P<day> [\d?]{1,2}) )?
        )?
        \s*
        (?: \[ (?P<qualifier>[^]]*) \])?
        '''
    our_re = re.compile(our_re_pat, re.VERBOSE)
    @classmethod
    def from_str(self, instr):
        '''Undo affect of __str__'''
        if not instr:
            return FlexiDate()

        out = self.our_re.match(instr)
        if out is None: # no match TODO: raise Exception?
            return None
        else:
            return FlexiDate(
                    out.group('year'),
                    out.group('month'),
                    out.group('day'),
                    qualifier=out.group('qualifier')
                    )
    
    def as_float(self):
        '''Get as a float (year being the integer part).

        Replace '?' in year with 9 so as to be conservative (e.g. 19?? becomes
        1900) and elsewhere (month, day) with 0
        '''
        if not self.year: return None
        out = float(self.year.replace('?', '9'))
        if self.month:
            # TODO: we are assuming months are of equal length
            out += float(self.month.replace('?', '0')) / 12.0
            if self.day:
                out += float(self.day.replace('?', '0')) / 365.0
        return out

# TODO: support for quarters e.g. Q4 1980 or 1954 Q3
# TODO: support latin stuff like M.DCC.LIII  
# TODO: convert '-' to '?' when used that way
# e.g. had this date [181-]
def parse(date):
    if not date:
        return None
    if isinstance(date, FlexiDate):
        return date
    if isinstance(date, int):
        return FlexiDate(year=date)
    elif isinstance(date, datetime.date):
        parser = PythonDateParser()
        return parser.parse(date)
    else: # assuming its a string
        parser = DateutilDateParser()
        out = parser.parse(date)
        if out is not None:
            return out
        # msg = 'Unable to parse %s' % date
        # raise ValueError(date)
        val = 'UNPARSED: %s' % date
        val = val.encode('ascii', 'ignore')
        return FlexiDate(qualifier=val)


class DateParserBase(object):
    def parse(self, date):
        raise NotImplementedError

    def norm(self, date):
        return str(self.parse(date))

class PythonDateParser(object):
    def parse(self, date):
        return FlexiDate(date.year, date.month, date.day)

try:
    import dateutil.parser
    dateutil_parser = dateutil.parser.parser()
except:
    dateutil_parser = None

class DateutilDateParser(DateParserBase):
    def parse(self, date):
        qualifiers = []
        if dateutil_parser is None:
            return None
        date = orig_date = date.strip()

        # various normalizations
        # TODO: call .lower() first
        date = date.replace('B.C.', 'BC')
        date = date.replace('A.D.', 'AD')

        # deal with pre 0AD dates
        if date.startswith('-') or 'BC' in date or 'B.C.' in date:
            pre0AD = True
        else:
            pre0AD = False
        # BC seems to mess up parser
        date = date.replace('BC', '')

        # deal with circa: 'c.1950' or 'c1950'
        circa_match = re.match('(.*)c\.?\s*(\d+.*)', date)
        if circa_match:
            # remove circa bit
            qualifiers.append("Note 'circa'")
            date = ''.join(circa_match.groups())

        # Deal with uncertainty: '1985?'
        uncertainty_match = re.match('([0-9xX]{4})\?', date)
        if uncertainty_match:
            # remove the ?
            date = date[:-1]
            qualifiers.append('Uncertainty')

        # Parse the numbers intelligently
        # do not use std parser function as creates lots of default data
        res = dateutil_parser._parse(date)

        if res is None:
            # Couldn't parse it
            return None
        #Note: Years of less than 3 digits not interpreted by
        #      dateutil correctly
        #      e.g. 87 -> 1987
        #           4  -> day 4 (no year)
        # Both cases are handled in this routine
        if res.year is None and res.day:
            year = res.day
        # If the whole date is simply two digits then dateutil_parser makes
        # it '86' -> '1986'. So strip off the '19'. (If the date specified
        # day/month then a two digit year is more likely to be this century
        # and so allow the '19' prefix to it.)
        elif len(date) == 2 or date.startswith('00'):
            year = res.year % 100
        else:
            year = res.year

        # finally add back in BC stuff
        if pre0AD:
            year = -year
            
        if not qualifiers:
            qualifier = ''
        else:
            qualifier = ', '.join(qualifiers) + (' : %s' % orig_date)
        return FlexiDate(year, res.month, res.day, qualifier=qualifier)
    
