#!/usr/bin/env python

"""
Copyright (c) 2006-2015 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""
import re
import base64
import json
import pickle
import sys
import binascii
from thirdparty import six

# IS_WIN = subprocess.mswindows
UNICODE_ENCODING = "utf8"

def base64decode(value):
    """
    Decodes string value from Base64 to plain format

    >>> base64decode('Zm9vYmFy')
    'foobar'
    """

    return base64.b64decode(value)

def base64encode(value):
    """
    Encodes string value from plain to Base64 format

    >>> base64encode('foobar')
    'Zm9vYmFy'
    """

    return base64.b64encode(value)

def base64pickle(value):
    """
    Serializes (with pickle) and encodes to Base64 format supplied (binary) value

    >>> base64pickle('foobar')
    'gAJVBmZvb2JhcnEALg=='
    """

    retVal = None

    try:
        retVal = base64encode(pickle.dumps(value, pickle.HIGHEST_PROTOCOL))
    except:
        warnMsg = "problem occurred while serializing "
        warnMsg += "instance of a type '%s'" % type(value)
        singleTimeWarnMessage(warnMsg)

        try:
            retVal = base64encode(pickle.dumps(value))
        except:
            retVal = base64encode(pickle.dumps(str(value), pickle.HIGHEST_PROTOCOL))

    return retVal

def base64unpickle(value):
    """
    Decodes value from Base64 to plain format and deserializes (with pickle) its content

    >>> base64unpickle('gAJVBmZvb2JhcnEALg==')
    'foobar'
    """

    retVal = None

    try:
        retVal = pickle.loads(base64decode(value))
    except TypeError: 
        retVal = pickle.loads(base64decode(bytes(value)))

    return retVal

def hexdecode(value):
    """
    Decodes string value from hex to plain format

    >>> hexdecode('666f6f626172')
    'foobar'
    """

    value = value.lower()
    return (value[2:] if value.startswith("0x") else value).decode("hex")

def hexencode(value):
    """
    Encodes string value from plain to hex format

    >>> hexencode('foobar')
    '666f6f626172'
    """

    return utf8encode(value).encode("hex")

def unicodeencode(value, encoding=None):
    """
    Returns 8-bit string representation of the supplied unicode value

    >>> unicodeencode(u'foobar')
    'foobar'
    """

    retVal = value
    if isinstance(value, unicode):
        try:
            retVal = value.encode(encoding or UNICODE_ENCODING)
        except UnicodeEncodeError:
            retVal = value.encode(UNICODE_ENCODING, "replace")
    return retVal

def utf8encode(value):
    """
    Returns 8-bit string representation of the supplied UTF-8 value

    >>> utf8encode(u'foobar')
    'foobar'
    """

    return unicodeencode(value, "utf-8")

def utf8decode(value):
    """
    Returns UTF-8 representation of the supplied 8-bit string representation

    >>> utf8decode('foobar')
    u'foobar'
    """

    return value.decode("utf-8")

def htmlunescape(value):
    """
    Returns (basic conversion) HTML unescaped value

    >>> htmlunescape('a&lt;b')
    'a<b'
    """

    retVal = value
    if value and isinstance(value, basestring):
        codes = (('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'), ('&nbsp;', ' '), ('&amp;', '&'))
        retVal = reduce(lambda x, y: x.replace(y[0], y[1]), codes, retVal)
    return retVal

def singleTimeWarnMessage(message):  # Cross-linked function
    sys.stdout.write(message)
    sys.stdout.write("\n")
    sys.stdout.flush()

def stdoutencode(data):
    retVal = None

    try:
        data = data or ""

        # Reference: http://bugs.python.org/issue1602
        if IS_WIN:
            output = data.encode(sys.stdout.encoding, "replace")

            if '?' in output and '?' not in data:
                warnMsg = "cannot properly display Unicode characters "
                warnMsg += "inside Windows OS command prompt "
                warnMsg += "(http://bugs.python.org/issue1602). All "
                warnMsg += "unhandled occurances will result in "
                warnMsg += "replacement with '?' character. Please, find "
                warnMsg += "proper character representation inside "
                warnMsg += "corresponding output files. "
                singleTimeWarnMessage(warnMsg)

            retVal = output
        else:
            retVal = data.encode(sys.stdout.encoding)
    except:
        retVal = data.encode(UNICODE_ENCODING) if isinstance(data, unicode) else data

    return retVal

def jsonize(data):
    """
    Returns JSON serialized data

    >>> jsonize({'foo':'bar'})
    '{\\n    "foo": "bar"\\n}'
    """

    return json.dumps(data, sort_keys=False, indent=4)

def dejsonize(data):
    """
    Returns JSON deserialized data

    >>> dejsonize('{\\n    "foo": "bar"\\n}')
    {u'foo': u'bar'}
    """

    return json.loads(data)

def getBytes(value, encoding=UNICODE_ENCODING, errors="strict", unsafe=True):
    """
    Returns byte representation of provided Unicode value

    >>> getBytes(u"foo\\\\x01\\\\x83\\\\xffbar") == b"foo\\x01\\x83\\xffbar"
    True
    """

    retVal = value

    if isinstance(value, six.text_type):
        retVal = value.encode(encoding, errors)

        if unsafe:
            retVal = re.sub(b"\\\\x([0-9a-f]{2})", lambda _: decodeHex(_.group(1)), retVal)

    return retVal


def getOrds(value):
    """
    Returns ORD(...) representation of provided string value

    >>> getOrds(u'fo\\xf6bar')
    [102, 111, 246, 98, 97, 114]
    >>> getOrds(b"fo\\xc3\\xb6bar")
    [102, 111, 195, 182, 98, 97, 114]
    """

    return [_ if isinstance(_, int) else ord(_) for _ in value]


def getText(value):
    """
    Returns textual value of a given value (Note: not necessary Unicode on Python2)

    >>> getText(b"foobar")
    'foobar'
    >>> isinstance(getText(u"fo\\u2299bar"), six.text_type)
    True
    """

    retVal = value

    if isinstance(value, six.binary_type):
        retVal = getUnicode(value)

    if six.PY2:
        try:
            retVal = str(retVal)
        except:
            pass

    return retVal


def decodeHex(value, binary=True):
    """
    Returns a decoded representation of provided hexadecimal value

    >>> decodeHex("313233") == b"123"
    True
    >>> decodeHex("313233", binary=False) == u"123"
    True
    """

    retVal = value

    if isinstance(value, six.binary_type):
        value = getText(value)

    if value.lower().startswith("0x"):
        value = value[2:]

    try:
        retVal = codecs.decode(value, "hex")
    except LookupError:
        retVal = binascii.unhexlify(value)

    if not binary:
        retVal = getText(retVal)

    return retVal