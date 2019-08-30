import re
import binascii
from lib.utils.common import getUnicode
from lib.utils.convert import decodeHex,getBytes,getOrds



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