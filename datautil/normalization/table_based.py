import gdata.spreadsheet.text_db

def _transform_key(key):
    return key.lower().strip()

class Normalizer(object):
    
    def __init__(self, username, password, doc_id, sheet, key_row):
        self.client = gdata.spreadsheet.text_db.DatabaseClient(
                      username=username, password=password)
        self._get_table(doc_id, sheet)
        self.key_row = key_row
        self._records = None

    @property
    def records(self):
        if self._records is None:
            self._records = [r.content for r in self.table.FindRecords('')]
        return self._records

    def _get_table(self, doc_id, sheet):
        db = self.client.GetDatabases(doc_id)[0]
        self.table = db.GetTables(name=sheet)[0]
        self.table.LookupFields()
    
    def keys(self): 
        return set([r.get(self.key_row) for r in self.records \
                    if r.get(self.key_row) is not None])
    
    def __contains__(self, item):
        return item in self.keys()

    def get(self, key, source_hint=None):
        if key is None:
            return {}
        record = self.lookup(key)
        if record:
            return record
        return self.add(_transform_key(key), source_hint).content
    
    def lookup(self, key):
        if key is None: 
            return {}
        local_key = _transform_key(unicode(key))
        for record in self.records: 
            # TODO #1: figure out FindRecords syntax
            # TODO #2: fuzzy matching for longer keys
            if record.get(self.key_row) == local_key:
                return record


    def add(self, value, source_hint):
        fields = self.table.fields
        row = dict(zip(fields, [None] * len(fields)))
        row[self.key_row] = value
        if source_hint is not None:
            row['source'] = source_hint
        self._records.append(row)
        return self.table.AddRecord(row)
        
class NormalizerJoin(object):
    
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def get(self, key, source_hint=None):
        if key in self.second:
            return self.second.get(key)
        data = self.first.get(key, source_hint=source_hint)
        if self.second.key_row in data:
            data.update(self.second.get(data.get(self.second.key_row)))
        return data
    
def Licenses(username, password):
    doc_id = 'thlRT-WO0EVweyjiwtYLslA'
    first = Normalizer(username, password, doc_id, 'Forms', 'original')
    second = Normalizer(username, password, doc_id, 'Licenses', 'code')
    return NormalizerJoin(first, second)

def Formats(username, password):
    doc_id = 'tO-VTk7QwloOt0EP3YpCC4A'
    first = Normalizer(username, password, doc_id, 'Forms', 'original')
    second = Normalizer(username, password, doc_id, 'Formats', 'mimetype')
    return NormalizerJoin(first, second)


