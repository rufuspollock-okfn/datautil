from StringIO import StringIO
import swiss.tabular.tabular_json as js

class TestJson:
    in1 = { 'header': [u'a', u'b'],
            'data': [[1,2], [3,4]]
            }
    in2 = [ in1['header'] ] + in1['data']
    in1sio = StringIO(js.json.dumps(in1))
    in1sio.seek(0)
    in2sio = StringIO(js.json.dumps(in2))
    in2sio.seek(0)

    def test_JsonReader(self):
        reader = js.JsonReader()
        out = reader.read(self.in1sio)
        assert out.header == self.in1['header']
        assert out.data == self.in1['data']

        out = reader.read(self.in2sio)
        assert out.header == self.in1['header']
        assert out.data == self.in1['data']

    def test_JsonWriter(self):
        writer = js.JsonWriter()
        td = js.TabularData(header=self.in1['header'], data=self.in1['data'])
        out = writer.write_str(td)
        assert js.json.loads(out) == self.in1

