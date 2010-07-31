'''Parse names of people into a standard format.'''

import re

titles = [
        u'Ayatollah',
        u'Baron',
        u'Bishop',
        u'Dame',
        u'Dr',
        u'Fr',
        u'Graf',
        u'King',
        u'Lady',
        u'Maj',
        u'Major',
        u'Mrs',
        u'Prof',
        u'Rev',
        u'Sir',
        u'St',
        ]

class Name(object):
    '''A name of a person or entity.
    
    Not a domain object but a convenient way to handle/parse names.

    Attributes:
        title
        ln: last name 
        firstnames: first names as list
    '''
    def __init__(self, ln='', fns=None, title=''):
        self.ln = ln
        self.fns = fns
        if self.fns is None: self.fns = []
        self.title = title

    def norm(self):
        '''Return normalised name string (LastFirst format)
        '''
        return name_tostr(self)        

    def __str__(self):
        '''Display name using normalised format
        '''
        return self.norm()

class NameParserBase(object):
    regex_remove_fullstops = re.compile(r'(\w{2,})\.(\W|$)', re.UNICODE)
    
    def parse(self, fullname):
        '''Parse the `fullname` string into a `Name` object.

        @return: `Name` object for `fullname`
        '''
        if fullname is None:
            return Name()
        fullname = unicode(fullname.strip())
        if not fullname:
            return Name()

        # remove words ending '.', e.g. 'Bosch.'
        fullname = self.regex_remove_fullstops.sub(r'\1\2', fullname)

        # make sure initials are separted by ' '
        # but first deal with special edge case like [Major.]
#        fullname = fullname.replace('.]', ']')
        fullname = fullname.replace('.', '. ')
        name = self._toparts(fullname)
        name.ln = self.normcase(name.ln)
        name.fns = [ self.normcase(x) for x in name.fns ]
        name.title = self.normcase(name.title)
        return name

    def _toparts(self, fullname):
        '''Implement in inheriting classes, called by parse.
        '''
        raise NotImplementedError()

    def tostr(self, name):
        '''Convert name object back into a string.
        '''
        raise NotImplementedError()

    def normcase(self, name): 
        # useful to handle none and you often get this from regexes
        if name is None:
            return ''
        name = name.strip()
        if name.upper() == name or name.lower() == name:
            return name.capitalize()
        # avoid issues with e.g. McTaggart
        else:
            return name

    def untitlize(self, _str):
        '''Return title contained in _str if a title else return empty string.
        '''
        title = _str.strip()
        title = _str.strip('()')
        if title in titles:
            return title
        # always assume something in square brackets is a title
        elif title.startswith('[') and title.endswith(']'):
            return title[1:-1].strip()
        else:
            return ''

    def titlize(self, _str):
        return u'[' + _str + u']'

    def norm(self, date):
        return str(self.parse(date))


class LastFirst(NameParserBase):
    '''Parse and creates names of form:

        lastname, first-names-in-order [title]
    '''
    def _toparts(self, fullname):
        if ',' not in fullname and ' ' in fullname:
            raise ValueError('Expected "," in name: %s' % fullname)
        name = Name()
        # NB: if more than 2 commas just ignore stuff after 2nd one
        parts = fullname.split(',')
        name.ln = parts[0]
        name.fns = parts[1].strip().split()
        if name.fns:
            title = self.untitlize(name.fns[-1])
            if title:
                name.title = title
                del name.fns[-1]
        return name

    def tostr(self, name):
        if name.ln or name.fns:
            fns = ' '.join(name.fns)
            if not fns:
                out = name.ln
            else:
                out = unicode(', '.join((name.ln, ' '.join(name.fns))))
        else:
            return ''
        if name.title:
            out = out + u' [%s]' % name.title
        return out


class FirstLast(NameParserBase):
    '''Parse and create names of form:

        [title] first-names last-name
    '''
    def _toparts(self, fullname):
        name = Name()
        if ',' in fullname:
            raise ValueError('Should not have "," in FirstLast type name: %s' %
                    fullname)
        parts = fullname.split()
        name.ln = parts[-1]
        name.fns = parts[:-1]
        if name.fns:
            title = self.untitlize(name.fns[0])
            if title:
                name.title = title
                del name.fns[0]
        return name

    def tostr(self, name):
        if name.fns or name.ln:
            out = u' '.join(name.fns) + ' ' + name.ln
        else:
            return ''
        if name.title:
            out = u'[%s]' % name.title + out
        return out


def parse_name(fullname):
    if ',' in fullname:
        parser = LastFirst()
    else:
        parser = FirstLast()
    return parser.parse(fullname)

def name_tostr(name, parser_class=LastFirst):
    parser = parser_class()
    return parser.tostr(name)

def normalize(name_str, parser_class=LastFirst):
    name = parse_name(name_str)
    return name_tostr(name, parser_class)


