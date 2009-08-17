import StringIO

from swiss.tabular.txt import *
from swiss.tabular import TabularData, CsvReader

class TestFormatting:

    sample_rows  = [
            ['1', '2', 'head blah', 'blah blah blah'],
            ['a', 'b', 'c', 'd', 'e', 'g' ],
            ['1', '2', 'annakarenina annakarenina annakarenina'],
            ]
    output_width = 60

    writer = TxtWriter(output_width=output_width)
    writer._compute_parameters(sample_rows)

    def test_1(self):
        assert self.writer.numcols == 6

    def test_colwidths(self):
        exp = int ((self.output_width -1) / 6)
        assert self.writer.colwidths[0] == exp
        
    def test__write_1(self):
        out = self.writer._write_row(self.sample_rows[0])
        assert len(out) <= self.output_width

    def test__write_2(self):
        out = self.writer._write_row(self.sample_rows[0])
        exp = '|   1    |   2    |head bla|blah bla|        |        |\n'
        assert out == exp

    def test__write_separator(self):
        out = self.writer._write_separator()
        exp = '+--------+--------+--------+--------+--------+--------+\n'



class TestTxtWriter:
    sample = \
'''"YEAR","PH","RPH","RPH_1","LN_RPH","LN_RPH_1","HH","LN_HH"
    1971,7.852361625,43.9168370988587,42.9594500501036,3.78229777955476,3.76025664867788,16185,9.69184016636035
    ,,abc,
    1972,10.504714885,55.1134791192682,43.9168370988587,4.00939431635556,3.78229777955476,16397,9.70485367024987
    , ,,  '''

    expected = \
'''+------+------+------+------+------+------+------+------+
| YEAR |  PH  | RPH  |RPH_1 |LN_RPH|LN_RPH|  HH  |LN_HH |
+------+------+------+------+------+------+------+------+
| 1971 |7.8523|43.916|42.959|3.7822|3.7602|16185 |9.6918|
+------+------+------+------+------+------+------+------+
|      |      | abc  |      |      |      |      |      |
+------+------+------+------+------+------+------+------+
| 1972 |10.504|55.113|43.916|4.0093|3.7822|16397 |9.7048|
+------+------+------+------+------+------+------+------+
|      |      |      |      |      |      |      |      |
+------+------+------+------+------+------+------+------+
'''

    def test_simple(self):
        indata = TabularData(data=[range(5),range(5,10)])
        writer = TxtWriter()
        out = writer.write_str(indata)
        exp = '''+-+-+-+-+-+
|0|1|2|3|4|
+-+-+-+-+-+
|5|6|7|8|9|
+-+-+-+-+-+
'''
        print out
        print exp
        assert out == exp

    def test_output_width(self):
        indata = TabularData(data=[range(5),range(5,10)])
        writer = TxtWriter(output_width=16)
        out = writer.write_str(indata)
        outlen = len(out.splitlines()[0])
        assert outlen == 16, outlen

    def test_using_csv(self):
        fileobj = StringIO.StringIO(self.sample)
        in_tdata = CsvReader(fileobj).read()
        writer = TxtWriter(output_width=60)
        out = writer.write_str(in_tdata)
        print out
        print self.expected
        assert self.expected == out, out

