'''A local file cache with url retrieving builtin.

NB: this module has zero dependencies on modules outside of the
standard lib so that it is easily reusable in other libraries and applications
that do not require any other parts of the datautil package.
'''
import urlparse
import urllib
import os
import sys


# have to define before Cache as used in classmethod
class _Progress(object):
    def __init__(self):
        self.count = -1

    def dl_progress(self, count, block_size, total_size):
        if total_size == 0: # total_size is weird so return to avoid errors
            return
        if self.count == -1:
            print 'Total size: %s' % self.format_size(total_size)
        last_percent = int(self.count*block_size*100/total_size)
        percent = int(count*block_size*100/total_size)
        if percent > last_percent:
            # TODO: is this acceptable? Do we want to do something nicer?
            sys.stdout.write('.')
            sys.stdout.flush()
        self.count = count

    def format_size(self, bytes):
        if bytes > 1000*1000:
            return '%.1fMb' % (bytes/1000.0/1000)
        elif bytes > 10*1000:
            return '%iKb' % (bytes/1000)
        elif bytes > 1000:
            return '%.1fKb' % (bytes/1000.0)
        else:
            return '%ibytes' % bytes


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

    def retrieve(self, url, overwrite=False):
        '''Retrieve url into cache and return the local path to it.
       
        :param url: url to retrieve.
        '''
        dest = self.cache_path(url)
        self.download(url, dest, overwrite)
        return dest

    def cache_path(self, url):
        '''Local path for url within cache.'''
        name = self.basename(url)
        dest = os.path.join(self.path, name)
        return dest

    def filepath(self, url):
        '''Deprecated: use cache_path'''
        return self.cache_path(url)

    def stream(self, url):
        fp = self.cache_path(url)
        if not os.path.exists(fp):
            return None
        else:
            return open(fp)
    
    @classmethod
    def basename(self, url):
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        result = path.split('/')[-1]
        if query:
            # escape '/' as otherwise path problems
            result += '?' + query.replace('/', '%47')
        return result

    @classmethod
    def download(self, url, dest, overwrite=False):
        '''Download a file from a url.

        :param url: the source url
        :param dest: the destination path to save to.
        :param overwrite: overwrite destination file if it exists (defaults to
            False).
        '''
        if not os.path.exists(dest) or overwrite:
            print 'Retrieving %s' % url 
            prog = _Progress()
            urllib.urlretrieve(url, dest, reporthook=prog.dl_progress)
        else:
            print 'Skipping download as dest already exists: %s' % url

    # for backwards compatability
    @classmethod
    def dl(self, url, dest=None):
        return self.download(url, dest)

