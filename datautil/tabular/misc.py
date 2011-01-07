'''General Helper methods for tabular data.
'''
from base import TabularData

def transpose(data):
    '''Transpose a list of lists.
    
    Or do it directy: data = zip(*data)
    '''
    return zip(*data)

def select_columns(matrix, cols):
    '''Return a matrix with only those column indexes in cols.'''
    tsp = transpose(matrix)
    out = []
    cols.sort()
    for c in cols:
        out.append(tsp[c])
    return transpose(out)


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

