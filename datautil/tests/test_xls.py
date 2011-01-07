import pkg_resources

import datautil.tabular

class TestXlsReader:

    def test_stuff(self):
        fo = pkg_resources.resource_stream('datautil',
            'tests/data/xls_reader_test.xls')
        reader = datautil.tabular.XlsReader(fo)
        tab = reader.read()
        assert tab.data[0][0] == 1850
        assert tab.data[19][1] == 12.3

