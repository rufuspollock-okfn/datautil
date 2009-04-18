import tempfile
import shutil
import os

from swiss.cache import Cache

class TestCache:
    @classmethod
    def setup_class(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, 'abc.txt')
        open(self.path, 'w').write('abc')
        self.url = 'file://%s' % self.path

    @classmethod
    def teardown_class(self):
        shutil.rmtree(self.tmp)

    def test_basename(self):
        base = 'http://www.abc.org/'
        in1 = base + 'xyz'
        out = Cache.basename(in1)
        assert out == 'xyz'

        in2 = base + 'xyz/abc.txt'
        out = Cache.basename(in2)
        assert out == 'abc.txt'

        in3 = base + 'membersDo?body=ABC'
        out = Cache.basename(in3)
        assert out == 'membersDo?body=ABC', out

    def test_filepath(self):
        r = Cache()
        base = 'http://www.abc.org/'
        in1 = base + 'xyz'
        out = r.filepath(in1)
        # ./xyz
        assert out.endswith('xyz'), out

    def test_dl(self):
        dest = os.path.join(self.tmp, 'out.txt')
        Cache.dl(self.url, dest)
        assert os.path.exists(dest)
        assert open(dest).read() == 'abc'

    def test_cache(self):
        cache = os.path.join(self.tmp, 'cache')
        r = Cache(cache)
        r.retrieve(self.url)
        assert os.path.exists(os.path.join(cache, 'abc.txt'))

