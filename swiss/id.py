import base64
import uuid

def compress_uuid(_uuid):
    '''Provided shortened string representation of UUID via base64 encoding.

    @return: 22 character base64 encoded version of UUID.
    '''
    if isinstance(_uuid, basestring):
        _uuid = uuid.UUID(_uuid)
    encode = base64.b64encode(_uuid.bytes, '_-')
    # throw away trailing ==
    return encode[:22]

def uncompress_uuid(b64_encoded):
    '''Reverse compress_uuid

    @return: 36 char str representation of uuid.
    '''
    b64_encoded = str(b64_encoded)
    if not b64_encoded.endswith('=='):
        b64_encoded += '=='
    out = base64.b64decode(b64_encoded, '_-')
    _uuid = uuid.UUID(bytes=out)
    return str(_uuid)


import struct
def int_to_b32(int_):
    out = struct.pack('1i', int_)
    out = base64.b32encode(out)
    # throw away trailing '='
    return out[:-1]

def b32_to_int(b32):
    out = base64.b32decode(b32+'=', casefold=True)
    out = struct.unpack('1i', out)[0]
    return out

