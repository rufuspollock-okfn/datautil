import os
from ConfigParser import SafeConfigParser

import swiss.tabular.gdocs as gdocs


cfg = SafeConfigParser()
if not os.path.exists('test.ini'):
    msg = 'To run these tests you need a config file. See this file for details'
    raise Exception(msg)
cfg.readfp(open('test.ini'))
username = cfg.get('gdocs', 'username')
password = cfg.get('gdocs', 'password')


class TestGDocsTextDb:
    def test_01(self):
        source = 'okfn-swiss-gdocs-testing'
        reader = gdocs.GDocsReaderTextDb(source, username, password, id_is_name=True)
        tdata = reader.read()
        assert tdata.header == ['col1', 'col2']
        assert len(tdata.data) == 5, tdata


# not working properly yet
class _TestGDocs:
    def test_01(self):
        source = 't8GZy4Lb6jhVjCL5nrqZ5TQ'
        reader = gdocs.GDocsReaderSpreadsheet(source, username, password)
        tdata = reader.read()
        assert len(tdata.data) == 6, tdata

    def test_02_id_is_name(self):
        source = 'okfn-swiss-gdocs-testing'
        reader = gdocs.GDocsReaderSpreadsheet(source, username, password, id_is_name=True)
        tdata = reader.read()
        assert len(tdata.data) == 6, tdata


