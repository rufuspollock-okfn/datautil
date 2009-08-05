# TODO: create a strict option where None is returned on failed convert rather
# than original value
placeholders = [ '', '-', '#' ]
def floatify(value):
    '''Convert value to a float if possible.

    @return: Floatified value. If value is blank or placeholder ('-') return
    None. Can deal with ',' in value. Will also floatify dates. If nothing
    works returns original value. 
    '''
    if value is None:
        return None
    if isinstance(value, basestring):
        stripped = value.strip()
        if not stripped or stripped in placeholders:
            return None
        else: 
            # often numbers have commas in them like 1,030
            v = value.replace(',', '')
    try:
        newval = float(v)
        return newval
    except:
        pass
    # will return original value if fails
    return date_to_float(value)

def floatify_matrix(matrix):
    return [ [ floatify(col) for col in row ] for row in matrix ]

# TODO: remove/convert to using date.FlexiDate.as_float()
import datetime
def date_to_float(date):
    '''Convert a date to float.

    Accepts either a date object or a string parseable to a date object
    
    @return: converted value or original if conversion fails
    '''
    import dateutil.parser
    if isinstance(date, basestring):
        try: # simple year
            return float(date)
        except:
            pass
        try:
            val = dateutil.parser.parse(date, default=datetime.date(1,1,1))
        except:
            return date
    else:
        val = date

    if isinstance(val, datetime.date):
        fval = val.year + val.month / 12.0 + val.day / 365.0
        return round(fval, 3)
    else:
        return val

def make_series(matrix, xcol, ycols=None):
    '''Take a matrix and return series (i.e. list of tuples) corresponding to
    specified column indices.

    E.g. if matrix is:
        [ [1,2,3,4]
          [5,6,7,8] ]
   
    and xcol = 0, ycols=[1,3] then output is:

    [
        [ [1,2], [5,6] ],
        [ [1,4], [5,8] ],
    ]

    If ycols not defined then return all possible series (excluding xcol
    with itself.
    '''
    cols = zip(*matrix)
    if ycols is None:
        ycols = range(len(cols))
        del ycols[xcol]
    cols = floatify_matrix(cols)
    def is_good(value):
        if value is None: return False
        tv = str(value)
        stopchars = [ '', '-' ]
        if tv in stopchars:
            return False
        return True
    def is_good_tuple(tuple):
        return is_good(tuple[0]) and is_good(tuple[1])
    
    xcoldata = cols[xcol]
    ycols = [ cols[ii] for ii in ycols ]
    series = [ filter(is_good_tuple, zip(xcoldata, col)) for col in ycols ]
    return series

