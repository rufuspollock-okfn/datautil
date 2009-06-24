import pkg_resources

import swiss.tabular

class TestXlsReader:

    def test_stuff(self):
        fo = pkg_resources.resource_stream('swiss',
            'tests/data/xls_reader_test.xls')
        reader = swiss.tabular.XlsReader(fo)
        tab = reader.read()
        assert tab.data[0][0] == 1850
        assert tab.data[19][1] == 12.3

