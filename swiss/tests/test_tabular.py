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


class TestTranspose:

    def test_1(self):
        inlist = [
                [ 0, 1 ],
                [ 1, 0 ],
                ]
        exp = [
                ( 0, 1 ),
                ( 1, 0 ),
                ]
        out = swiss.tabular.transpose(inlist)
        assert out == exp, out

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
        writer.write(fo, td)
        fo.seek(0)
        out = fo.read()
        exp = \
'''one,two\r
1,2\r
3,4\r\n'''
        assert out == exp


# TODO: reenable
# TODO: sort out a smaller xls_reader_test.xls file
class _TestXlsReader:

    def test_stuff(self):
        fp = os.path.dirname(__file__)
        fp = os.path.join(fp, 'xls_reader_test.xls')
        fo = open(fp)
        reader = swiss.tabular.XlsReader()
        tab = reader.read(fo)
        assert tab.data[0][0] == 1850
        assert tab.data[19][1] == 12.3


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


class TestWriterHtml:

    def setUp(self):
        rawData = [[1,1], [0,1]]
        self.indata1 = swiss.tabular.TabularData(data=rawData)
        self.writer1 = swiss.tabular.WriterHtml({'id':1, 'class': 'data'})

    def testSimple(self):
        indata1 = [[1,1], [0,1]]
        expected = '<table id="1" class="data"><tbody><tr><td>1</td><td>1</td></tr>'+\
            '<tr><td>0</td><td>1</td></tr></tbody></table>'
        out1 = self.writer1.write(self.indata1)
        assert expected == out1
    
    def testColHeadings(self):
        self.indata1.header = [u'x','y']
        caption = ''
        expected = '<table id="1" class="data"><thead><tr><th>x</th><th>y</th></tr>'+\
            '</thead><tbody><tr><td>1</td><td>1</td></tr><tr><td>0</td>' + \
            '<td>1</td></tr></tbody></table>'
        # no caption but headings
        out1 = self.writer1.write(self.indata1, caption)
        assert expected == out1
    
    def testRowHeadings(self):
        self.indata1.header = ['x','y']
        rowHeadings = ['Date 1', 'Date 2']
        caption = ''
        expected = '<table id="1" class="data"><thead><tr><th></th><th>x</th>' + \
            '<th>y</th></tr></thead><tbody><tr><th>Date 1</th><td>1</td>' + \
            '<td>1</td></tr><tr><th>Date 2</th><td>0</td><td>1</td></tr>' + \
            '</tbody></table>'
        # no caption but headings
        out1 = self.writer1.write(self.indata1, caption, rowHeadings)
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
        out = self.m2l.write(td)
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


class TestPivot:
    td = swiss.tabular.TabularData(
            header=['Name','Year','Value'],
            data=[
                ['x',2004,1],
                ['y',2004,2],
                ['y',2005,4],
                ['x',2005,3],
            ],
        )

    def test_pivot_with_tabular(self):
        out = swiss.tabular.pivot(self.td, 1, 0, 2)
        assert out.data[0] == [2004, 1, 2]
        assert out.data[-1] == [2005, 3, 4]

    def test_pivot_with_tabular_2(self):
        out = swiss.tabular.pivot(self.td, 'Year', 'Name', 'Value')
        assert out.data[0] == [2004, 1, 2]

    def test_pivot_simple_list(self):
        out = swiss.tabular.pivot(self.td.data, 1, 0, 2)
        assert out.data[0] == [2004, 1, 2]

