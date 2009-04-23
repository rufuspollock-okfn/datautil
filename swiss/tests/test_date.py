from pdw.date import *

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

    def test_ordering(self):
        fd1 = FlexiDate(2000, 6, 1)
        fd2 = FlexiDate(2000)
        assert str(fd2) < str(fd1)

        fd3 = FlexiDate(1999, qualifier='c.')
        assert str(fd3) < str(fd2)

        fd4  = FlexiDate(-1000)
        assert str(fd4) < str(fd3)

        fd5 = FlexiDate(-10000)
        # assert str(fd5) < str(fd4), '%s, %s' % (fd5, fd4)


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

        
    
    def test_parse_with_qualifiers(self):
        # TODO: get this working
        fd = parse('1985?')
        # assert fd.year == u'1985', fd
        # assert fd.qualifier == u'?', fd
        fd = parse('c.1780')
        # assert fd.year == u'1780', fd
        # assert fd.qualifier == u'c.', fd

