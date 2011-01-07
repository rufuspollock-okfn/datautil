'''Work with Excel (xls) files.

Requires xlrd
'''
try:
    import xlrd
except ImportError: # xlrd not installed
    pass

from base import ReaderBase, TabularData

class XlsReader(ReaderBase):
    '''Read Excel (xls) files.

    Requires the xlrd package (see pypi).
    '''
    def __init__(self, filepath_or_fileobj=None):
        super(XlsReader, self).__init__(filepath_or_fileobj)
        if self.fileobj:
            self.book = xlrd.open_workbook(file_contents=self.fileobj.read())
        ## TODO: fix the rest of this

    def read(self, fileobj=None, sheet_index=0):
        '''Read an excel file (provide as fileobj) and return the specified
        sheet as a L{TabularData} object.

        For convenience also store:

        self.book: xlrd WorkBook object
        
        @return L{TabularData} object.
        '''
        super(XlsReader, self).read(fileobj)
        if fileobj:
            self.book = xlrd.open_workbook(file_contents=self.fileobj.read())
        tab = TabularData()
        booksheet = self.book.sheet_by_index(sheet_index)
        data = self.extract_sheet(booksheet, self.book)
        tab.data = data
        return tab

    def info(self):
        '''Return summary info about this Excel Workbook.'''
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
        sh = self.book.sheet_by_index(sheet_index)
        info = sh.name + '\n'
        info += 'Rows: %s Cols: %s\n\n' % (sh.nrows, sh.ncols)
        MAX_ROWS = 30
        for rx in range(min(sh.nrows, MAX_ROWS)):
            info += str(sh.row(rx)) + '\n'
        return info

    def extract_sheet(self, sheet, book):
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


