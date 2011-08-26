import re
import unicodedata
import string

KILL_DASHES = re.compile("\\-+")

def compose(text):
    return unicodedata.normalize('NFKC', text)
    
def decompose(text):
    return unicodedata.normalize('NFKD', text)

def recompose(text):
    return compose(decompose(text))

def url_slug(text):
    """ Convert arbitrary text to something that can be a url slug. """
    out = []
    for c in decompose(text):
        cat = unicodedata.category(c)[0].upper()
        if cat == 'Z':
            out.append('-')
        if c in string.ascii_letters or c in string.digits:
            out.append(c)
        if c in ['-', '.', '+', '_']:
            out.append(c)
    text = u"".join(out).lower()
    return KILL_DASHES.sub('-', text)


