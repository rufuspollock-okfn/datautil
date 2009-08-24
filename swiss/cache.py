'''A local file cache with url retrieving builtin.

NB: this module has zero dependencies on modules outside of the
standard lib so that it is easily reusable in other libraries and applications
that do not require any other parts of the swiss package.
'''
import urlparse
import urllib
import os

class Cache(object):
    '''A local file cache (and url retriever).
    '''
    def __init__(self, path='.'):
        '''
        @param path: path to cache (defaults to current directory)
        '''
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(path)

    def retrieve(self, url, force=False):
        '''Retrieve url into cache and return the local path to it.'''
        dest = self.cache_path(url)
        if not os.path.exists(dest) or force:
            self.dl(url, dest)
        return dest

    def cache_path(self, url):
        '''Local path for url within cache.'''
        name = self.basename(url)
        dest = os.path.join(self.path, name)
        return dest

    def filepath(self, url):
        '''Deprecated: use cache_path'''
        return self.cache_path(url)

    @classmethod
    def basename(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        result = path.split('/')[-1]
        if query:
            result += '?' + query
        return result

    @classmethod
    def dl(self, url, dest=None):
        '''Download a file from a url.
        '''
        if not dest:
            dest = self.basename(url)
        urllib.urlretrieve(url, dest)

