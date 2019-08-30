import re
import binascii

# from convert import getBytes
# from convert import getOrds
# from convert import getUnicode
def getUnicode(value, encoding=None, noneToNull=False):

    """
    Return the unicode representation of the supplied value:

    >>> getUnicode(u'test')
    u'test'
    >>> getUnicode('test')
    u'test'
    >>> getUnicode(1)
    u'1'
    """

    if noneToNull and value is None:
        return 'NULL'

    # if isListLike(value):
    #     value = list(getUnicode(_, encoding, noneToNull) for _ in value)
    #     return value

    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        while True:
            try:
                return unicode(value, encoding or 'utf8')
            except UnicodeDecodeError, ex:
                try:
                    return unicode(value, UNICODE_ENCODING)
                except:
                    value = value[:ex.start] + "".join(INVALID_UNICODE_CHAR_FORMAT % ord(_) for _ in value[ex.start:ex.end]) + value[ex.end:]
    else:
        try:
            return unicode(value)
        except UnicodeDecodeError:
            return unicode(str(value), errors="ignore")  # encoding ignored for non-basestring instances

def decodeHex(value, binary=True):
    """
    Returns a decoded representation of provided hexadecimal value

    >>> decodeHex("313233") == b"123"
    True
    >>> decodeHex("313233", binary=False) == u"123"
    True
    """

    retVal = value

    # if isinstance(value, six.binary_type):
    #     value = getText(value)

    if value.lower().startswith("0x"):
        value = value[2:]

    try:
        retVal = codecs.decode(value, "hex")
    except LookupError:
        retVal = binascii.unhexlify(value)

    # if not binary:
    #     retVal = getText(retVal)

    return retVal

def getBytes(value, encoding='utf8', errors="strict", unsafe=True):
    """
    Returns byte representation of provided Unicode value

    >>> getBytes(u"foo\\\\x01\\\\x83\\\\xffbar") == b"foo\\x01\\x83\\xffbar"
    True
    """

    retVal = value

    if isinstance(value, str):
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

def escaper(value):
            if all(_ < 128 for _ in getOrds(value)):
                return "0x%s" % getUnicode(binascii.hexlify(getBytes(value)))
            else:
                return "CONVERT(0x%s USING utf8)" % getUnicode(binascii.hexlify(getBytes(value)))

def _escape(expression, quote=True):
        retVal = expression

        if quote:
            for item in re.findall(r"'[^']*'+", expression):
                original = item[1:-1]
                if original and re.search(r"\[(SLEEPTIME|RAND)", original) is None:  # e.g. '[SLEEPTIME]' marker
                    replacement = escaper(original)

                    if replacement != original:
                        retVal = retVal.replace(item, replacement)
                    elif len(original) != len(getBytes(original)) and "n'%s'" % original not in retVal:
                        retVal = retVal.replace("'%s'" % original, "n'%s'" % original)
        else:
            retVal = escaper(expression)

        return retVal

exp = "CONCAT('qzkkq','YJQqKeZsgBnpTVdAPgtnhNSPswhMEAsvlhOhPqKD','qpkvq')"
print _escape(exp)