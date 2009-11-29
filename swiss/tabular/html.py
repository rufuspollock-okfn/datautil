import re
from HTMLParser import HTMLParser

from base import TabularData, ReaderBase, WriterBase


class HtmlReader(ReaderBase):
    '''Read data from HTML table into L{TabularData}.

    '''
    def read(self, filepath_or_fileobj=None, table_index=0):
        '''Read data from fileobj.

        NB: post read all tables extracted are in attribute named 'tables'.

        @arg table_index: if multiple tables in the html return table at this
            index.
        @return: L{TabularData} object (all content in the data part, i.e. no
        header).
        '''
        super(HtmlReader, self).read(filepath_or_fileobj)
        parser = _OurTableExtractor()
        parser.reset()
        parser.feed(self.fileobj.read())
        self.tables = parser.tables
        return self.tables[table_index]


class _OurTableExtractor(HTMLParser):
    '''
    # TODO: tbody, thead etc
    # TODO: nested tables

    # TODO: will barf on bad html so may need to run tidy first ...
    # tidy -w 0 -b -omit -asxml -ascii
    '''
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
            self.tables.append(TabularData(data=self._rows))
            self._rows = []

    def handle_data(self, data):
        self._text += data.strip()

    
import re
class HtmlWriter(WriterBase):
    """
    Write tabular data to xhtml
    """
    
    def __init__(self, round_ndigits=2, pretty_print=False, table_attributes = {'class': 'data'}):
        """
        @pretty_print: whether to pretty print (indent) output
        @table_attributes: dictionary of html attribute name/value pairs to be
        added to the table element
        """
        super(HtmlWriter, self).__init__(round_ndigits)
        self.pretty_print = pretty_print
        self.table_attributes = table_attributes
    
    def write(self, tabulardata, fileobj, caption = '', rowHeadings = []):
        """
        Write matrix of data to xhtml table.
        Allow for addition of row and column headings
        
        @return xhtml table containing data
        
        @param data: table of data that makes up table
        @param caption: the caption for the table (if empty no caption created)
        @param rowHeadings: additional headings for rows (separate from
        tabulardata)
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
            htmlTable += '<caption>%s</caption>' % caption
        
        # deal with col headings
        # if we there are rowHeadings may want to add blank column at front
        numColHeads = len(columnHeadings)
        if numColHeads > 0:
            if haveRowHeadings and numColHeads == len(data[0]):
                # [[TODO: is this dangerous? should i make a copy ...]]
                columnHeadings.insert(0, '')
            htmlTable += self.writeHeading(columnHeadings)
        
        htmlTable += '<tbody>'
        if self.pretty_print:
            htmlTable += '\n'
        
        for ii in range(0, len(data)):
            # have to add 1 as first row is headings
            if haveRowHeadings:
                htmlTable += self.writeRow(data[ii], rowHeadings[ii])
            else:
                htmlTable += self.writeRow(data[ii])
        
        htmlTable += '</tbody></table>'
        
        if self.pretty_print:
            fileobj.write(self.prettyPrint(htmlTable))
        else:
            fileobj.write(htmlTable)

    def value_to_str(self, value):
        import cgi
        out = super(HtmlWriter, self).value_to_str(value)
        out = cgi.escape(out)
        return out
        
    def writeHeading(self, row):
        """
        Write heading for html table (<thead>)
        """
        result = '<thead><tr>'
        result += self.writeGeneralRow(row, 'th')
        result += '</tr></thead>'
        if self.pretty_print:
            result += '\n'
        return result
    
    def writeRow(self, row, rowHeading = ''):
        result = ''
        if rowHeading != '':
            result = '<th>%s</th>' % self.value_to_str(rowHeading)
        result += self.writeGeneralRow(row, 'td')
        result = '<tr>%s</tr>' % result
        if self.pretty_print:
            result += '\n'
        return result
    
    def writeGeneralRow(self, row, tagName):
        result = ''
        for ii in range(len(row)):
            result += '<%s>%s</%s>' % (tagName, self.value_to_str(row[ii]), tagName)
        return result
        
    def prettyPrint(self, html):
        """pretty print html using HTMLTidy"""
        # [[TODO: strip out html wrapper stuff that is added (head, body etc)
        try:
            import mx.Tidy
            out = mx.Tidy.tidy(html, None, None, wrap = 0, indent = 'yes')[2]
        except:
            out = html
        return self.tabify(out)
        
    def tabify(self, instr, tabsize = 2):
        """
        tabify text by replacing spaces of size tabSize by tabs
        """
        whitespace = tabsize * ' '
        return re.sub(whitespace, '\t', instr)
        
    
# for backwards compatibility
# 2008-05-30
WriterHtml = HtmlWriter


