from swiss.misc import *

class TestFloatify:
    def test_floatify_1(self):
        x = '10'
        assert floatify(x) == 10.0

    def test_floatify_2(self):
        x = '1,030'
        assert floatify(x) == 1030.0

    def test_floatify_2(self):
        x = ''
        out = floatify(x)
        assert out == None, out
        x = '#'
        out = floatify(x)
        assert out == None, out

    def test_floatify_matrix(self):
        x = [ 
                ['1', '2'],
                ['abc', '3.0']
                ]
        exp = [ 
                [1.0, 2.0],
                ['abc', 3.0]
                ]
        out = floatify_matrix(x)
        assert out == exp


class TestMakeSeries:

    def test_make_series(self):
        indata = [ [ '1980', '100', '50' ],
                [ '1981', '101', '51' ],
                [ '1982', '102', '' ],
                ]
        exp = [
                [ (1980.0, 100.0), (1981.0, 101.0), (1982.0, 102.0) ],
                [ (1980.0, 50.0), (1981.0, 51.0) ]
            ]
        out = make_series(indata, xcol=0, ycols=[1,2])
        assert out == exp, out

