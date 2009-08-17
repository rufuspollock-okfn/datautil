import os
from StringIO import StringIO

import swiss.tabular

class TestTabularData:
    testlist = [ ['X', 'Y'], [1,2], [3,4] ]

    def test_1(self):
        tabular = swiss.tabular.TabularData()
        assert tabular.header == []

    def test_from_list(self):
        out = swiss.tabular.TabularData.from_list(self.testlist)
        assert out.header == [ 'X', 'Y' ]
        assert out.data == [ [1,2], [3,4] ]

    def test_to_list(self):
        td = swiss.tabular.TabularData(
            header=['X', 'Y'],
            data=[ [1,2], [3,4] ]
            )
        out = td.to_list()
        assert out == self.testlist


class TestWriterBase:
    def test_value_to_str(self):
        w = swiss.tabular.WriterBase() # round_ndigits=None
        out = w.value_to_str('x')
        assert out == u'x', out
        out = w.value_to_str(1)
        assert out == u'1', out
        out = w.value_to_str(1.3555)
        assert out == u'1.3555', out

        w = swiss.tabular.WriterBase(round_ndigits=2)
        out = w.value_to_str('x')
        assert out == u'x', out
        out = w.value_to_str(1)
        assert out == u'1', out
        out = w.value_to_str(1.3555)
        assert out == u'1.36', out

        w.round_ndigits = -1
        out = w.value_to_str(102.34)
        assert out == u'100', out


class TestReaderCsv(object):
    
    csvdata = \
'''"header1", "header 2"
1, 2'''
    header = [ 'header1', 'header 2' ]
    data = [ ['1', '2'] ]
  
    def setUp(self):
        reader = swiss.tabular.ReaderCsv()
        fileobj = StringIO(self.csvdata)
        self.tab = reader.read(fileobj)

    def test_header(self):
        assert self.header == self.tab.header

    def test_data(self):
        assert self.data == self.tab.data


class TestReaderCsvUnicode(TestReaderCsv):
    csvdata = \
u'''"headi\xf1g", "header 2"
1, 2'''
    header = [ u'headi\xf1g'.encode('utf-8'), 'header 2' ]
    data = [ ['1', '2'] ]


class TestReaderCsvEncoded(TestReaderCsvUnicode):
    encoding = 'utf-16'
    csvdata = \
u'''"headi\xf1g", "header 2"
1, 2'''.encode(encoding)

    def setUp(self):
        reader = swiss.tabular.ReaderCsv()
        fileobj = StringIO(self.csvdata)
        self.tab = reader.read(fileobj, encoding=self.encoding)


class TestCsvWriter:
    def test_writer(self):
        writer = swiss.tabular.CsvWriter()
        fo = StringIO()
        td = swiss.tabular.TabularData([[1,2],[3,4]], header=['one',
            'two'])
        writer.write(td, fo)
        fo.seek(0)
        out = fo.read()
        exp = \
'''one,two\r
1,2\r
3,4\r\n'''
        assert out == exp


class TestHtmlReader:

    inraw1 = '''
<table>
    <tr>
        <td>1</td><td>2</td>
    </tr>
    <tr>
        <th colspan="2">1983</th>
    </tr>
    <tr>
        <td>3</td><td>4</td>
    </tr>
</table>
    '''
    in1 = StringIO(inraw1)
    
    exp1 = [ ['1', '2'],
            ['1983'],
            ['3', '4'],
            ]
    
    def test_1(self):
        reader = swiss.tabular.HtmlReader()
        tab = reader.read(self.in1)
        assert tab.data == self.exp1


class TestHtmlWriter:

    def setUp(self):
        rawData = [[1,1], [0,1]]
        self.indata1 = swiss.tabular.TabularData(data=rawData)
        self.writer1 = swiss.tabular.HtmlWriter(table_attributes={'id':1, 'class': 'data'})

    def test_0_simple(self):
        indata1 = [[1,1], [0,1]]
        expected = '<table id="1" class="data"><tbody><tr><td>1</td><td>1</td></tr>'+\
            '<tr><td>0</td><td>1</td></tr></tbody></table>'
        out1 = self.writer1.write_str(self.indata1)
        assert expected == out1
    
    def test_col_headings(self):
        self.indata1.header = [u'x','y']
        caption = ''
        expected = '<table id="1" class="data"><thead><tr><th>x</th><th>y</th></tr>'+\
            '</thead><tbody><tr><td>1</td><td>1</td></tr><tr><td>0</td>' + \
            '<td>1</td></tr></tbody></table>'
        # no caption but headings
        out1 = self.writer1.write_str(self.indata1, caption)
        assert expected == out1
    
    def test_row_headings(self):
        self.indata1.header = ['x','y']
        rowHeadings = ['Date 1', 'Date 2']
        caption = ''
        expected = '<table id="1" class="data"><thead><tr><th></th><th>x</th>' + \
            '<th>y</th></tr></thead><tbody><tr><th>Date 1</th><td>1</td>' + \
            '<td>1</td></tr><tr><th>Date 2</th><td>0</td><td>1</td></tr>' + \
            '</tbody></table>'
        # no caption but headings
        out1 = self.writer1.write_str(self.indata1, caption, rowHeadings)
        assert expected == out1
    
#    def testPrettyPrint(self):
#        in1 = '<table><tr><th>x</th><th>y</th></tr>' + \
#            '<tr><td>0</td><td>1</td></tr></table>'
#        print self.writer1.prettyPrint(in1)


class TestLatexWriter:

    matrix = [[ 'H1', 'H2'],
           [1,'2%'],
           [3,4],
           ]

    exp = \
r'''\textbf{H1} & \textbf{H2} \\
\hline
1 & 2\% \\
\hline
3 & 4 \\
\hline
'''
    m2l = swiss.tabular.LatexWriter()

    def test_escape(self):
        in1 = '& % $ something'
        exp1 = r'\& \% $ something'
        assert self.m2l.escape(in1) == exp1

    def test_table2latex(self):
        out = swiss.tabular.table2latex(self.matrix)
        self.diff(self.exp, out)
        assert out == self.exp

    def test_write(self):
        td = swiss.tabular.TabularData(data=self.matrix[1:], header=self.matrix[0])
        out = self.m2l.write_str(td)
        self.diff(self.exp, out)
        assert out == self.exp

    def diff(self, str1, str2):
        import difflib
        differ = difflib.Differ()
        text1 = str1.splitlines(1)
        text2 = str2.splitlines(1)
        result = list(differ.compare(text1, text2))
        from pprint import pprint
        pprint(result)


