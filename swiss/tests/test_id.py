import uuid

import swiss.id

def test_compress_and_uncompress():
    hexversion = '86c3f19d-8854-4ef5-8d88-f008e0817871'

    out = swiss.id.compress_uuid(hexversion)
    assert len(out) == 22

    orig = swiss.id.uncompress_uuid(out)
    assert orig == hexversion

    # test unicode
    orig = swiss.id.uncompress_uuid(unicode(out))
    assert orig == hexversion

    u1 = uuid.UUID(hexversion)
    out = swiss.id.compress_uuid(u1)
    assert len(out) == 22

