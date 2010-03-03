'''TabularData from a Google Docs Spreadsheet.
'''
from base import ReaderBase, TabularData
import gdata.spreadsheet.service
import gdata.spreadsheet.text_db


class GDocsReaderTextDb(ReaderBase):
    '''Read a google docs spreadsheet using the gdata.spreadsheet.text_db
    library.
    
    NB: any blank line in spreadsheet will be taken as terminating data.
    '''
    def __init__(self, spreadsheet_id, username=None, password=None,
            id_is_name=False):
        '''
        @param: spreadsheet_id: gdoc id or name (?key={id} in url). If name you
        must set id_is_name to True.
        '''
        # do not pass spreadsheet_id down as it will be url or sheet name
        super(GDocsReaderTextDb, self).__init__()
        self.source = spreadsheet_id
        self.id_is_name = id_is_name
        self.gd_client = gdata.spreadsheet.text_db.DatabaseClient(
                username=username,
                password=password)
    
    def load_text_db_table(self, sheet_name='Sheet1'):
        '''Load text_db Table object corresponding to specified sheet_name.
        '''
        super(GDocsReaderTextDb, self).read(None)
        if self.id_is_name:
            dbs = self.gd_client.GetDatabases(name=self.source)
            assert len(dbs) >= 1, 'No spreadsheet of that name/id'
        db = dbs[0]
        table = db.GetTables(name=sheet_name)[0]
        return table

    def read(self, sheet_name='Sheet1'):
        '''Load the specified google spreadsheet worksheet as a L{TabularData}
        object.

        @return L{TabularData} object.
        '''
        text_db_table = self.load_text_db_table(sheet_name)
        tdata = TabularData()
        text_db_table.LookupFields()
        tdata.header = text_db_table.fields
        # finds all records it seems
        rows = text_db_table.FindRecords('')
        for row in rows:
            rowdata = []
            for colname in tdata.header:
                rowdata.append(row.content[colname])
            tdata.data.append(rowdata)
        return tdata


# not yet working properly (cannot work out ListFeed yet ...)
# textdb is nicer but Spreadsheet allows one to get all cells using CellsFeed
# (even when blank lines) (this is not true when using ListFeed though ...)
# class GDocsReaderSpreadsheet(ReaderBase):
#     '''
# 
#     From Docs for the API:
#     <http://code.google.com/apis/spreadsheets/data/1.0/developers_guide_python.html#listFeeds>
# 
#     > The list feed contains all rows after the first row up to the first blank
#     row. The first blank row terminates the data set. If expected data isn't
#     appearing in a feed, check the worksheet manually to see whether there's an
#     unexpected blank row in the middle of the data. In particular, if the
#     second row of the spreadsheet is blank, then the list feed will contain no
#     data.
#     '''
#     def __init__(self, spreadsheet_id, username=None, password=None,
#             id_is_name=False):
#         '''
#         @param: spreadsheet_id: gdoc id or name (?key={id} in url). If name you
#         must set id_is_name to True.
#         '''
#         # do not pass spreadsheet_id down as it will be url or sheet name
#         super(GDocsReaderSpreadsheet, self).__init__()
#         self.source = spreadsheet_id
#         self.id_is_name = id_is_name
#         self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
#         self.gd_client.email = username
#         self.gd_client.password = password
# 
#     def read(self, sheet_index=0):
#         '''Load the specified google spreadsheet worksheet as a L{TabularData}
#         object.
# 
#         @return L{TabularData} object.
#         '''
#         super(GDocsReaderSpreadsheet, self).read(None)
#         self.gd_client.source = self.source
#         self.gd_client.ProgrammaticLogin()
#         if self.id_is_name:
#             feed = self.gd_client.GetSpreadsheetsFeed()
#             # no len on feed ...
#             # assert len(feed) > 0, 'No spreadsheets found for: %s' % self.source
#             spreadsheet_id = feed.entry[0].id.text.split('/')[-1]
#         else:
#             spreadsheet_id = self.source
#         sheetfeed = self.gd_client.GetWorksheetsFeed(spreadsheet_id)
#         wrksht_id = sheetfeed.entry[sheet_index].id.text.split('/')[-1]
#         row_feed = self.gd_client.GetListFeed(spreadsheet_id, wrksht_id)
#         
#         tdata = TabularData()
#         # tdata.header
#         # how do we get rows rather than just all the cells?
#         for i, entry in enumerate(row_feed.entry):
#             print entry.content['col1']
#             print entry.content
#             tdata.data.append([entry.content.text])
#         return tdata

