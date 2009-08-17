from base import WriterBase

class TxtWriter(WriterBase):
    '''Write tabular data to plain text in nicely formatted way

TODO
====

1. allow output_width of 0 meaning use width necessary to fit all rows on one
   line

2. rather than truncate cell contents wrap it onto two lines (and/or allow
   spillover if adjacent cell is empty)
   
     * wontfix: can let terminal do this: just set width very large ...

3. (?) stream output back rather than returning all at once

4. Add support for limiting number of columns displayed. DONE 2007-08-02
   * TODO: add unittest
'''

    def __init__(self, output_width=0, number_of_columns=0, **kwargs):
        '''
        @param output_width: display width (0 means unlimited).
        @param number_of_columns: number of columns to try to display (not
            guaranteed to be this number if this would cause problems). (0
            means all columns)
        '''
        super(TxtWriter, self).__init__(**kwargs)
        self.output_width = output_width
        self.number_of_columns = number_of_columns

    def write(self, tabular_data, fileobj):
        result = ''
        formatter = None
        row_cache = []
        sample_length = 2
        rows = tabular_data.data
        if tabular_data.header:
            rows = [ tabular_data.header ] + rows
        # include header in sample rows (do we always want to?)
        sample_rows = rows[:sample_length]
        self._compute_parameters(sample_rows)
        result += self._write_separator()
        for row in rows:
            result += self._write_row(row)
            result += self._write_separator()
        fileobj.write(result)

    def _compute_parameters(self, sample_rows):
        maxcols = self._get_maxcols(sample_rows)
        if not self.number_of_columns:
            self.numcols = maxcols
        else:
            self.numcols = min(self.number_of_columns, maxcols)
        self.colwidths = []
        self._set_colwidths(sample_rows)
        if self.colwidths[0] < 2:
            msg =\
'''It is not possible to effectively format this many columns of material with
this narrow an output window. Column width is: %s''' % self.colwidths[0]
            raise ValueError(msg)

    def _write_row(self, row):
        '''Return the input 'python' row as an appropriately formatted string.
        '''
        result = '|'
        count = 0
        for cell in row[:self.numcols]:
            width = self.colwidths[count]
            result += self._format_cell(width, cell)
            count += 1
        # now pad out with extra cols as necessary
        while count < self.numcols:
            width = self.colwidths[count]
            result += self._format_cell(width, ' ')
            count += 1
        return result + '\n'

    def _write_separator(self):
        result = '+'
        for width in self.colwidths:
            result += '-' * (width-1) + '+'
        return result + '\n'

    def _get_maxcols(self, sample_rows):
        maxcols = 0
        for row in sample_rows:
            maxcols = max(maxcols, len(row))
        return maxcols

    def _set_colwidths(self, sample_rows):
        # subtract -1 so that we have (at least) one spare screen column
        if self.output_width != 0:
            colwidth = int( (self.output_width - 1) / self.numcols)
            for ii in range(self.numcols):
                self.colwidths.append(colwidth)
        else: # make every col as wide as it needs to be
            self.colwidths = [0] * self.numcols
            for row in sample_rows:
                for ii in range(self.numcols):
                    cellwidth = len(self.value_to_str(row[ii]))
                    self.colwidths[ii] = max(self.colwidths[ii],
                            cellwidth
                            )
            self.colwidths = [ x + 1 for x in self.colwidths ]

    def _format_cell(self, width, content):
        content = self.value_to_str(content)
        content = content.strip()
        if len(content) > width - 1:
            # TODO: be brutal (this *has* to be fixed)
            content = content[:width-1]
        return content.center(width-1) + '|'

