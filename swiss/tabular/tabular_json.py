'''JSON Reader and Writer'''
try:
    import json
except:
    import simplejson as json


from base import TabularData, ReaderBase, WriterBase

class JsonReader(ReaderBase):
    def read(self, filepath_or_fileobj=None):
        '''Read JSON encoded data from source into a L{TabularData} object.

        JSON encoded data should either be:
            * dict (with header and data attributes)
            * list (first row assumed to be the header)

        @return L{TabularData}
        '''
        super(JsonReader, self).read(filepath_or_fileobj)
        jsondata = json.load(self.fileobj)
        if isinstance(jsondata, dict):
            return TabularData(header=jsondata.get('header', None),
                    data=jsondata.get('data', None)
                    )
        elif isinstance(jsondata, list):
            return TabularData(header=jsondata[0], data=jsondata[1:])
        else:
            raise Exception('Cannot load TabularData from %s' % jsondata)

class JsonWriter(WriterBase):

    def write(self, tabular_data, fileobj, indent=2):
        super(JsonWriter, self).write(tabular_data, fileobj)
        jsondata = { u'header': tabular_data.header,
                u'data': tabular_data.data
                }
        json.dump(jsondata, fileobj, indent=indent)

