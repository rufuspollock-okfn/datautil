from swiss.date import *

import datetime

class TestPythonStringOrdering(object):
    # It is impossible to find a string format such that +ve and -ve numbers
    # sort correctly as strings:
    # if (in string ordering) X < Y => -X < -Y (False!)
    def test_ordering(self):
        assert '0' < '1'
        assert '-10' < '10'
        assert '-' < '@'
        assert '-' < '0'
        assert '-100' < '-X10'
        assert '10' < '1000'
        assert '02000' < '10000'
        assert ' 2000' < '10000'

    def test_bad_ordering(self):
        assert ' ' < '0'
        assert ' ' < '-'
        assert not '-' < '+'
        assert '-100' > '-10'
        assert not '-100' < '-010'
        assert not '-100' < '- 10'
        assert not '-100' < ' -10'
        assert '10000' < '2000'
        assert not '-10' < ' 1'
        

class TestFlexiDate(object):
    def test_init(self):
        fd = FlexiDate()
        assert fd.year == '', fd
        assert fd.month == '', fd

        fd = FlexiDate(2000, 1,1)
        assert fd.month == '01', fd
        assert fd.day== '01', fd

    def test_str(self):
        fd = FlexiDate(2000, 1, 23)
        assert str(fd) == '2000-01-23', '"%s"' % fd
        fd = FlexiDate(-2000, 1, 23)
        assert str(fd) == '-2000-01-23'
        fd = FlexiDate(2000)
        assert str(fd) == '2000'
        fd = FlexiDate(1760, qualifier='fl.')
        assert str(fd) == '1760 [fl.]', fd

        fd = FlexiDate(qualifier='anything')
        assert str(fd) == ' [anything]'


    def test_from_str(self):
        def dotest(fd):
            out = FlexiDate.from_str(str(fd))
            assert str(out) == str(fd)

        fd = FlexiDate(2000, 1, 23)
        dotest(fd)
        fd = FlexiDate(1760, qualifier='fl.')
        dotest(fd)
        fd = FlexiDate(-1760, 1, 3, qualifier='fl.')
        dotest(fd)
    
    def test_as_float(self):
        fd = FlexiDate(2000)
        assert fd.as_float() == float(2000), fd.as_float()
        fd = FlexiDate(1760, 1, 2)
        exp = 1760 + 1/12.0 + 2/365.0
        assert fd.as_float() == exp, fd.as_float()
        fd = FlexiDate(-1000)
        assert fd.as_float() == float(-1000)


class TestDateParsers(object):
    def test_using_datetime(self):
        parser = PythonDateParser()

        d1 = datetime.date(2000, 1, 23)
        fd = parser.parse(d1)
        assert fd.year == '2000'

        d1 = datetime.datetime(2000, 1, 23)
        fd = parser.parse(d1)
        # assert str(fd) == '2000-01-23T00:00:00', fd
        assert str(fd) == '2000-01-23', fd

    def test_using_dateutil(self):
        parser = DateutilDateParser()

        in1 = '2001-02'
        fd = parser.parse(in1)
        assert str(fd) == in1, fd

        in1 = 'March 1762'
        fd = parser.parse(in1)
        assert str(fd) == '1762-03'

        in1 = 'March 1762'
        fd = parser.parse(in1)
        assert str(fd) == '1762-03'

        in1 = '1768 AD'
        fd = parser.parse(in1)
        assert str(fd) == '1768', fd

        in1 = '-1850'
        fd = parser.parse(in1)
        assert str(fd) == '-1850', fd

        in1 = '1762 BC'
        fd = parser.parse(in1)
        assert str(fd) == '-1762', fd

        in1 = '4 BC'
        fd = parser.parse(in1)
        assert str(fd) == '-0004', fd

    def test_parse(self):
        d1 = datetime.datetime(2000, 1, 23)
        fd = parse(d1)
        assert fd.year == '2000'

        fd = parse('March 1762')
        assert str(fd) == '1762-03'

        fd = parse(1966)
        assert str(fd) == '1966'

    def test_parse_with_none(self):
        d1 = parse(None)
        assert d1 is None
    
    def test_parse_with_qualifiers(self):
        # TODO: get this working
        fd = parse('1985?')
        # assert fd.year == u'1985', fd
        # assert fd.qualifier == u'?', fd
        fd = parse('c.1780')
        # assert fd.year == u'1780', fd
        # assert fd.qualifier == u'c.', fd

