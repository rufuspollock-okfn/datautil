"""
Tools for dealing with tabular data
"""

class TabularData(object):
    """Holder for tabular data

    NB:
      * Assume data organized in rows.
      * No type conversion so all data will be as entered.

    Properties:
      * data: data itself provided as array of arrays
      * header: associated header columns (if they exist)

    TODO: handling of large datasets (iterators?)
    """

    def __init__(self, data=None, header=None):
        """
        Initialize object. If data or header not set they are defaulted to
        empty list.
        
        NB: must use None as default value for arguments rather than []
        because [] is mutable and using it will result in subtle bugs. See:
        'Default parameter values are evaluated when the function definition
        is executed.' [http://www.python.org/doc/current/ref/function.html]
        """
        self.data = []
        self.header = []
        if data is not None:
            self.data = data
        if header is not None:
            self.header = header
    
    def __repr__(self):
        out = []
        if self.header:
            out.append(self.header)
        # limit to 10 items
        out += self.data[0:10]
        return repr(out)

    def __iter__(self):
        return self.data.__iter__()

class ReaderBase(object):
    def __init__(self, filepath_or_fileobj=None):
        self.filepath = None
        self.fileobj = None
        self._filepath_or_fileobj(filepath_or_fileobj)

    def _filepath_or_fileobj(self, filepath_or_fileobj):
        if filepath_or_fileobj is None: # do not overwrite any existing value
            pass
        elif isinstance(filepath_or_fileobj, basestring):
            self.filepath = filepath_or_fileobj
            self.fileobj = open(self.filepath)
        else:
            self.filepath = None
            self.fileobj = filepath_or_fileobj
    
    def read(self, filepath_or_fileobj=None):
        self._filepath_or_fileobj(filepath_or_fileobj)


def transpose(data):
    '''Transpose a list of lists.
    
    Or do it directy: data = zip(*data)
    '''
    return zip(*data)


import csv
import codecs
class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8

    From: <http://docs.python.org/lib/csv-examples.html>
    """
    def __init__(self, f, encoding=None):
        if encoding:
            self.reader = codecs.getreader(encoding)(f)
        else: # already unicode so just return f
            self.reader = f

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf-8')

class CsvReader(object):
    """Read data from a csv file into a TabularData structure

    Note that the csv module does *not* support unicode:
    
    > This version of the csv module doesn't support Unicode input. Also, there
    > are currently some issues regarding ASCII NUL characters. Accordingly,
    > all input should be UTF-8 or printable ASCII to be safe; see the examples
    > in section 9.1.5. These restrictions will be removed in the future.
    > <http://docs.python.org/lib/module-csv.html>

    Thus L{read} method requires uses an encoding.
    """

    def read(self, fileobj, encoding='utf-8'):
        """Read in a csv file and return a TabularData object

        @param fileobj: file like object.
        @param encoding: the encoding of the file like object. NB: will check
        if fileobj already in unicode in which case this is ignored.
        @return tabular data object (all values encoded as utf-8).
        """
        tabData = TabularData()

        sample = fileobj.read()
        # first do a simple test -- maybe sample is already unicode
        if type(sample) == unicode:
            encoded_fo = UTF8Recoder(fileobj, None)
        else:
            sample = sample.decode(encoding)
            encoded_fo = UTF8Recoder(fileobj, encoding)
        sample = sample.encode('utf-8')
        sniffer = csv.Sniffer()
        hasHeader = sniffer.has_header(sample)

        fileobj.seek(0)
        reader = csv.reader(encoded_fo, skipinitialspace=True)
        if hasHeader:
            tabData.header = reader.next()
        for row in reader:
            tabData.data.append(row)
        return tabData

# for backwards compatibility
ReaderCsv = CsvReader

class CsvWriter(object):
    # TODO: unicode support a la CsvReader
    def write(self, fileobj, tabular_data, encoding='utf-8'):
        writer = csv.writer(fileobj)
        if tabular_data.header:
            writer.writerow(tabular_data.header)
        for row in tabular_data.data:
            writer.writerow(row)
        fileobj.flush()


class XlsReader(ReaderBase):
    '''Read Excel (xls) files.

    Requires the xlrd package (see pypi).
    '''
    def __init__(self, filepath_or_fileobj=None):
        super(XlsReader, self).__init__(filepath_or_fileobj)
        ## TODO: fix the rest of this

    def read(self, fileobj=None, sheet_index=0):
        '''Read an excel file (provide as fileobj) and return the specified
        sheet as a L{TabularData} object.

        For convenience also store:

        self.book: xlrd WorkBook object
        
        @return L{TabularData} object.
        '''
        super(XlsReader, self).read(fileobj)
        import xlrd
        tab = TabularData()
        self.book = xlrd.open_workbook(file_contents=self.fileobj.read())
        booksheet = self.book.sheet_by_index(sheet_index)
        data = self.extract_sheet(booksheet, self.book)
        tab.data = data
        return tab

    def info(self):
        '''Return summary info about this Excel Workbook.'''
        import xlrd
        info = ''
        info += 'The number of worksheets is: %s\n' % self.book.nsheets
        info += 'Worksheet name(s):\n' % self.book.sheet_names()
        count = -1
        for sn in self.book.sheet_names():
            count += 1
            info += '%s  %s\n' % (count, sn)
        return info

    def sheet_info(self, sheet_index):
        '''Summary info about an xls sheet.

        @return: printable string giving info.
        '''
        import pprint
        import xlrd
        sh = self.book.sheet_by_index(sheet_index)
        info = sh.name + '\n'
        info += 'Rows: %s Cols: %s\n\n' % (sh.nrows, sh.ncols)
        MAX_ROWS = 30
        for rx in range(min(sh.nrows, MAX_ROWS)):
            info += str(sh.row(rx)) + '\n'
        return info

    def extract_sheet(self, sheet, book):
        import xlrd
        matrix = []
        nrows = sheet.nrows
        ncols = sheet.ncols
        for rx in range(nrows):
            outrow = []
            for cx in range(ncols):
                cell = sheet.cell(rowx=rx, colx=cx)
                val = self.cell_to_python(cell, book)
                outrow.append(val)
            matrix.append(outrow)
        return matrix

    def cell_to_python(self, cell, book):
        import xlrd
        # annoying need book argument for datemode
        # info on types: http://www.lexicon.net/sjmachin/xlrd.html#xlrd.Cell-class
        if cell.ctype == xlrd.XL_CELL_NUMBER: 
            return float(cell.value)
        elif cell.ctype == xlrd.XL_CELL_DATE:
            from datetime import date
            # TODO: distinguish date and datetime
            args = xlrd.xldate_as_tuple(cell.value, book.datemode)
            try:
                return date(args[0], args[1], args[2])
            except Exception, inst:
                print 'Error parsing excel date (%s): %s' % (args, inst)
                return None
        elif cell.ctype == xlrd.XL_CELL_BOOLEAN:
            return bool(cell.value)
        else:
            return cell.value


from HTMLParser import HTMLParser
class HtmlReader(HTMLParser):
    '''Read data from HTML table into L{TabularData}.

    # TODO: tbody, thead etc
    # TODO: nested tables

    # TODO: will barf on bad html so may need to run tidy first ...
    # tidy -w 0 -b -omit -asxml -ascii
    '''
    def read(self, fileobj, table_index=0):
        '''Read data from fileobj.

        NB: post read all tables extracted are in attribute named 'tables'.

        @arg table_index: if multiple tables in the html return table at this
            index.
        @return: L{TabularData} object (all content in the data part, i.e. no
        header).
        '''
        self.reset()
        self.feed(fileobj.read())
        tab = TabularData()
        tab.data = self.tables[table_index]
        return tab

    def reset(self):
        HTMLParser.reset(self)
        self.tables = []
        self._rows = []
        self._row = []
        self._text = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self._row = []
        elif tag == 'td' or tag == 'th':
            self._text = ''
        elif tag == 'br':
            self._text += '\n'

    def handle_endtag(self, tag):
        if tag == 'tr':
            self._rows.append(self._row)
        if tag == 'td' or tag == 'th':
            self._row.append(self._text)
        if tag == 'table':
            self.tables.append(self._rows)
            self._rows = []

    def handle_data(self, data):
        self._text += data.strip()

    
import re
class HtmlWriter(object):
    """
    Write tabular data to xhtml
    """
    
    def __init__(self, table_attributes = {'class': 'data'}, decimal_places=2, do_pretty_print=False):
        """
        @do_pretty_print: whether to pretty print (indent) output
        @attributes: dictionary of html attribute name/value pairs to be
        added to the table element
        @decimal_places: number of decimal places to use when rounding numerical 
                        values when textifying for table
        """
        self.do_pretty_print = do_pretty_print
        self.table_attributes = table_attributes
        self.decimal_places = decimal_places
    
    def write(self, tabulardata, caption = '', rowHeadings = []):
        """
        Write matrix of data to xhtml table.
        Allow for addition of row and column headings
        
        @return xhtml table containing data
        
        @param data: table of data that makes up table
        @param caption: the caption for the table (if empty no caption created)
        """
        columnHeadings = tabulardata.header
        data = tabulardata.data
        haveRowHeadings = (len(rowHeadings) > 0)
        
        htmlTable = '<table'
        for key, value in self.table_attributes.items():
            htmlTable += ' %s="%s"' % (key, value)
        htmlTable += '>'
        
        # deal with caption
        if caption != '':
            htmlTable += self._writeTag('caption', caption)
        
        # deal with col headings
        # if we there are rowHeadings may want to add blank column at front
        numColHeads = len(columnHeadings)
        if numColHeads > 0:
            if haveRowHeadings and numColHeads == len(data[0]):
                # [[TODO: is this dangerous? should i make a copy ...]]
                columnHeadings.insert(0, '')
            htmlTable += self.writeHeading(columnHeadings)
        
        htmlTable += '<tbody>'
        
        for ii in range(0, len(data)):
            # have to add 1 as first row is headings
            if haveRowHeadings:
                htmlTable += self.writeRow(data[ii], rowHeadings[ii])
            else:
                htmlTable += self.writeRow(data[ii])
        
        htmlTable += '</tbody></table>'
        
        if self.do_pretty_print:
            return self.prettyPrint(htmlTable)
        else:
            return htmlTable
        
    def writeHeading(self, row):
        """
        Write heading for html table (<thead>)
        """
        result = '<thead><tr>'
        result += self.writeGeneralRow(row, 'th')
        result += '</tr></thead>'
        return result
    
    def writeRow(self, row, rowHeading = ''):
        result = ''
        if rowHeading != '':
            result = self._writeTag('th', rowHeading)
        result += self.writeGeneralRow(row, 'td')
        result = self._writeTag('tr', result)
        return result
    
    def writeGeneralRow(self, row, tagName):
        result = ''
        for ii in range(len(row)):
            result += self._writeTag(tagName, row[ii])
        return result
        
    def prettyPrint(self, html):
        """pretty print html using HTMLTidy"""
        # [[TODO: strip out html wrapper stuff that is added (head, body etc)
        import mx.Tidy
        return self.tabify(mx.Tidy.tidy(html, None, None, wrap = 0,
            indent = 'yes')[2])
        
    def tabify(self, instr, tabsize = 2):
        """
        tabify text by replacing spaces of size tabSize by tabs
        """
        whitespace = tabsize * ' '
        return re.sub(whitespace, '\t', instr)
        
    def _writeTag(self, tagName, value):
        return '<' + tagName + '>' + self._processTagValueToText(value) + \
            '</' + tagName + '>'
    
    def _processTagValueToText(self, tagValue):
        # if not already text then round
        if tagValue is None:
            return ''
        elif isinstance(tagValue, int) or isinstance(tagValue, float):
            roundedResult = str(round(tagValue, self.decimal_places))
            # deal with case when rounding has added unnecessary digits
            if len(str(tagValue)) < len(roundedResult):
                return str(tagValue)
            else:
                return roundedResult
        else:
            return unicode(tagValue)

# for backwards compatibility
# 2008-05-30
WriterHtml = HtmlWriter

## ---------------------------------------------------------
## General Helper methods 

def select_columns(matrix, cols):
    '''Return a matrix with only those column indexes in cols.'''
    tsp = transpose(matrix)
    out = []
    cols.sort()
    for c in cols:
        out.append(tsp[c])
    return transpose(out)

def format_cols_as_ints(matrix, cols):
    for ii in range(len(matrix)):
        for col in cols:
            try: # ignore errors (dangerous maybe)
                matrix[ii][col] = '%d' % matrix[ii][col]
            except:
                pass
    return matrix

## --------------------------------
## Converting to Latex

class LatexWriter(object):

    def process_row(self, row, heading=False):
        if len(row) == 0: return
        out = '%s' % self.process_cell(row[0], heading or self.has_column_headings)
        for cell in row[1:]:
            out += ' & %s' % self.process_cell(cell, heading)
        out += ' \\\\\n\hline\n'
        return out

    def process_cell(self, cell, heading=False):
        cell_text = self.escape(unicode(cell))
        if heading:
            return '\\textbf{%s}' % cell_text
        else:
            return cell_text

    def escape(self, text):
        escape_chars = [ '&', '%' ]
        out = text
        for ch in escape_chars:
            out = out.replace(ch, '\\%s' % ch)
        return out
    
    def write(self, tabular_data, has_column_headings=False):
        matrix = tabular_data.data
        has_header = len(tabular_data.header) > 0
        if has_header: 
            matrix.insert(0, tabular_data.header)
        return self._write(matrix, has_header, has_column_headings)
    
    def _write(self, matrix, has_header=True, has_column_headings=False):
        self.has_column_headings = has_column_headings
        if len(matrix) == 0: return
        # no hline on first row as this seems to mess up latex \input
        # http://groups.google.com/group/comp.text.tex/browse_thread/thread/1e1db553a958ebd8/0e590a22cb59f43d
        out = '%s' % self.process_row(matrix[0], has_header)
        for row in matrix[1:]:
            out += self.process_row(row) 
        return out

def table2latex(matrix, has_header=True, has_column_headings=False):
    m2l = LatexWriter()
    return m2l._write(matrix, has_header, has_column_headings)

def pivot(table, left, top, value):
    """Unnormalize (pivot) a normalised input set of tabular data.

    @param table: simple list of lists or a L{TabularData} object.
    
    Eg. To transform the tabular data like
    
    Name,   Year,  Value
    -----------------------
    'x', 2004, 1
    'y', 2004, 2
    'x', 2005, 3
    'y', 2005, 4
    
    into the new list:
    
    Year, 'x', 'y'
    ------------------------
    2004, 1, 2
    2005, 3, 4
    
    you would do:

        pivot(tabulardata, 1, 0, 2)

        OR (requires header to exist):

        pivot(tabulardata, 'Year', 'Name', 'Value')
    """
    if not isinstance(left, int):
        left = table.header.index(left)
    if not isinstance(top, int):
        top = table.header.index(top)
    if not isinstance(value, int):
        value = table.header.index(value)

    rs = TabularData()
    # construct double dict keyed by left values
    tdict = {}
    xvals = set()
    yvals = set()
    for row in table:
        xval = row[left]
        if not xval in tdict:
            tdict[xval] = {}
        tdict[xval][row[top]] = row[value]
        xvals.add(xval)
        yvals.add(row[top])
    xvals = sorted(list(xvals))
    yvals = sorted(list(yvals))
    xhead = 'X'
    if hasattr(table, 'header') and table.header:
        xhead = table.header[left]
    rs.header = [ xhead ] + yvals
    rs.data = [ [x] + [ tdict[x].get(y, '') for y in yvals ] for x in xvals ]
    return rs

