from difflib import SequenceMatcher
from odict import OrderedDict

import re
import time
import random
import string
import urllib
import contextlib
import collections
from StringIO import StringIO
import os
import codecs
from math import sqrt
from xml.sax import parse
import types
import copy
from thirdparty import six
from thirdparty.six.moves import zip as _zip
from lib.config import conf,kb
from lib.data import AttribDict
from lib.utils.bigarray import BigArray
from lib.utils.enums import PLACE, CUSTOM_INJECTION_MARK_CHAR, UNICODE_ENCODING
from lib.utils.enums import PARAMETER_AMP_MARKER, PARAMETER_SEMICOLON_MARKER, DEFAULT_GET_POST_DELIMITER
from lib.utils.enums import TEXT_TAG_REGEX, REFLECTED_VALUE_MARKER,DBMS_DICT







cache = None


def cleanupVals(text, tag):
    if tag in ("clause", "where"):
        text = text.split(',')

    if isinstance(text, basestring):
        text = int(text) if text.isdigit() else str(text)

    elif isinstance(text, list):
        count = 0

        for _ in text:
            text[count] = int(_) if _.isdigit() else str(_)
            count += 1

        if len(text) == 1 and tag not in ("clause", "where"):
            text = text[0]

    return text

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

def urlencode(value, safe="%&=-_", convall=False, limit=False, spaceplus=False):
    """
    URL encodes given value

    >>> urlencode('AND 1>(2+3)#')
    'AND%201%3E%282%2B3%29%23'
    """

    count = 0
    result = None if value is None else ""

    if value:
        if convall or safe is None:
            safe = ""

        # corner case when character % really needs to be
        # encoded (when not representing URL encoded char)
        # except in cases when tampering scripts are used
        if all(map(lambda x: '%' in x, [safe, value])):
            value = re.sub("%(?![0-9a-fA-F]{2})", "%25", value)

        while True:
            result = urllib.quote(utf8encode(value), safe)

            if limit and len(result) > URLENCODE_CHAR_LIMIT:
                if count >= len(URLENCODE_FAILSAFE_CHARS):
                    break

                while count < len(URLENCODE_FAILSAFE_CHARS):
                    safe += URLENCODE_FAILSAFE_CHARS[count]
                    count += 1
                    if safe[-1] in value:
                        break
            else:
                break

        if spaceplus:
            result = result.replace(urllib.quote(' '), '+')

    return result

def randomStr(length=4, lowercase=False, alphabet=None, seed=None):
    """
    Returns random string value with provided number of characters

    >>> random.seed(0)
    >>> randomStr(6)
    'RNvnAv'
    """

    choice = random.WichmannHill(seed).choice if seed is not None else random.choice

    if alphabet:
        retVal = "".join(choice(alphabet) for _ in xrange(0, length))
    elif lowercase:
        retVal = "".join(choice(string.ascii_lowercase) for _ in xrange(0, length))
    else:
        retVal = "".join(choice(string.ascii_letters) for _ in xrange(0, length))

    return retVal

def checkFile(filename):
    """
    Checks for file existence and readability
    """

    valid = True

    if filename is None or not os.path.isfile(filename):
        valid = False

    if valid:
        try:
            with open(filename, "rb"):
                pass
        except:
            valid = False

    if not valid:
        print 1

def openFile(filename, mode='r', encoding=UNICODE_ENCODING, errors="replace", buffering=1):
    """
    Returns file handle of a given filename
    """

    try:
        return codecs.open(filename, mode, encoding, errors, buffering)
    except IOError:
        errMsg = "there has been a file opening error for filename '%s'. " % filename
        errMsg += "Please check %s permissions on a file " % ("write" if \
          mode and ('w' in mode or 'a' in mode or '+' in mode) else "read")
        errMsg += "and that it's not locked by another process."
        print 1

def readCachedFileContent(filename, mode='rb'):
    """
    Cached reading of file content (avoiding multiple same file reading)
    """
    # global cache 
    checkFile(filename)
    if conf.cache is None:
        with openFile(filename, mode) as f:
            conf.cache = f.read()

    return conf.cache

def parseXmlFile(xmlFile, handler):
    """
    Parses XML file by a given handler
    """

    try:
        with contextlib.closing(StringIO(readCachedFileContent(xmlFile))) as stream:
            parse(stream, handler)
    except Exception as ex:
        print ex

def findDynamicContent(firstPage, secondPage):
    """
    This function checks if the provided pages have dynamic content. If they
    are dynamic, proper markings will be made
    """

    if not firstPage or not secondPage:
        return

    blocks = SequenceMatcher(None, firstPage, secondPage).get_matching_blocks()
    dynamicMarkings = []

    # Removing too small matching blocks
    for block in blocks[:]:
        (_, _, length) = block

        if length <= DYNAMICITY_MARK_LENGTH:
            blocks.remove(block)

    # Making of dynamic markings based on prefix/suffix principle
    if len(blocks) > 0:
        blocks.insert(0, None)
        blocks.append(None)

        for i in xrange(len(blocks) - 1):
            prefix = firstPage[blocks[i][0]:blocks[i][0] + blocks[i][2]] if blocks[i] else None
            suffix = firstPage[blocks[i + 1][0]:blocks[i + 1][0] + blocks[i + 1][2]] if blocks[i + 1] else None

            if prefix is None and blocks[i + 1][0] == 0:
                continue

            if suffix is None and (blocks[i][0] + blocks[i][2] >= len(firstPage)):
                continue

            prefix = trimAlphaNum(prefix)
            suffix = trimAlphaNum(suffix)

            dynamicMarkings.append((re.escape(prefix[-DYNAMICITY_MARK_LENGTH / 2:]) if prefix else None, re.escape(suffix[:DYNAMICITY_MARK_LENGTH / 2]) if suffix else None))

    if len(dynamicMarkings) > 0:
        infoMsg = "dynamic content marked for removal (%d region%s)" % (len(dynamicMarkings), 's' if len(dynamicMarkings) > 1 else '')
        print infoMsg

def removeDynamicContent(page):
    """
    Removing dynamic content from supplied page basing removal on
    precalculated dynamic markings
    """

    dynamicMarkings = []
    if page:
        for item in dynamicMarkings:
            prefix, suffix = item

            if prefix is None and suffix is None:
                continue
            elif prefix is None:
                page = re.sub(r'(?s)^.+%s' % re.escape(suffix), suffix, page)
            elif suffix is None:
                page = re.sub(r'(?s)%s.+$' % re.escape(prefix), prefix, page)
            else:
                page = re.sub(r'(?s)%s.+%s' % (re.escape(prefix), re.escape(suffix)), '%s%s' % (prefix, suffix), page)

    return page

def isListLike(value):
    """
    Returns True if the given value is a list-like instance

    >>> isListLike([1, 2, 3])
    True
    >>> isListLike(u'2')
    False
    """

    return isinstance(value, (list, tuple, set, BigArray))

def urldecode(value, encoding=None, unsafe="%%&=;+%s" % CUSTOM_INJECTION_MARK_CHAR, convall=False, plusspace=True):
    """
    URL decodes given value

    >>> urldecode('AND%201%3E%282%2B3%29%23', convall=True)
    u'AND 1>(2+3)#'
    """

    result = value

    if value:
        try:
            # for cases like T%C3%BCrk%C3%A7e
            value = str(value)
        except ValueError:
            pass
        finally:
            if convall:
                result = urllib.unquote_plus(value) if plusspace else urllib.unquote(value)
            else:
                def _(match):
                    charset = reduce(lambda x, y: x.replace(y, ""), unsafe, string.printable)
                    char = chr(ord(match.group(1).decode("hex")))
                    return char if char in charset else match.group(0)
                result = value
                if plusspace:
                    result = result.replace("+", " ")  # plus sign has a special meaning in URL encoded data (hence the usage of
                                                       # urllib.unquote_plus in
                                                                                                            # convall case)
                result = re.sub("%([0-9a-fA-F]{2})", _, result)

    if isinstance(result, str):
        result = unicode(result, encoding or UNICODE_ENCODING, "replace")

    return result

def paramToDict_t(place, parameters=None):
    """
    Split the parameters into names and values, check if these parameters
    are within the testable parameters and return in a dictionary.
    """

    testableParameters = OrderedDict()

    parameters = re.sub(r"&(\w{1,4});", r"%s\g<1>%s" % (PARAMETER_AMP_MARKER, PARAMETER_SEMICOLON_MARKER), parameters)
    if place == PLACE.COOKIE:
        splitParams = parameters.split(DEFAULT_COOKIE_DELIMITER)
    else:
        splitParams = parameters.split(DEFAULT_GET_POST_DELIMITER)

    for element in splitParams:
        element = re.sub(r"%s(.+?)%s" % (PARAMETER_AMP_MARKER, PARAMETER_SEMICOLON_MARKER), r"&\g<1>;", element)
        parts = element.split("=")

        if len(parts) >= 2:
            parameter = urldecode(parts[0].replace(" ", ""))

            if not parameter:
                continue

            testableParameters[parameter] = "=".join(parts[1:])

   

    if testableParameters:
        for parameter, value in testableParameters.items():
            if value and not value.isdigit():
                for encoding in ("hex", "base64"):
                    try:
                        decoded = value.decode(encoding)
                        if len(decoded) > MIN_ENCODED_LEN_CHECK and all(_ in string.printable for _ in decoded):
                            warnMsg = "provided parameter '%s' " % parameter
                            warnMsg += "seems to be '%s' encoded" % encoding
                            logger.warn(warnMsg)
                            break
                    except:
                        pass

    return testableParameters

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
        return NULL

    if isListLike(value):
        value = list(getUnicode(_, encoding, noneToNull) for _ in value)
        return value

    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        while True:
            try:
                return unicode(value, encoding or UNICODE_ENCODING)
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

def randomInt(length=4, seed=None):
    """
    Returns random integer value with provided number of digits

    >>> random.seed(0)
    >>> randomInt(6)
    874254
    """

    choice = random.WichmannHill(seed).choice if seed is not None else random.choice

    return int("".join(choice(string.digits if _ != 0 else string.digits.replace('0', '')) for _ in xrange(0, length)))

def extractRegexResult(regex, content, flags=0):
    """
    Returns 'result' group value from a possible match with regex on a given
    content

    >>> extractRegexResult(r'a(?P<result>[^g]+)g', 'abcdefg')
    'bcdef'
    """

    retVal = None

    if regex and content and "?P<result>" in regex:
        match = re.search(regex, content, flags)

        if match:
            retVal = match.group("result")

    return retVal

#将参数分割到dict中去
#FixME:暂时不分割敏感字段，后期可以再做更新
def paramToDict(parameters=None):
    """
    Split the parameters into names and values, check if these parameters
    are within the testable parameters and return in a dictionary.
    """

    testableParameters = OrderedDict()

    """
    if place in conf.parameters and not parameters:
        parameters = conf.parameters[place]
    """

    parameters = re.sub(r"&(\w{1,4});", r"%s\g<1>%s" % (PARAMETER_AMP_MARKER, PARAMETER_SEMICOLON_MARKER), parameters)

    splitParams = parameters.split(None or '&')

    for element in splitParams:
        element = re.sub(r"%s(.+?)%s" % (PARAMETER_AMP_MARKER, PARAMETER_SEMICOLON_MARKER), r"&\g<1>;", element)
        parts = element.split("=")

        if len(parts) == 1:
            testableParameters[parts[0]] = ''
            continue

        if len(parts) >= 2:
            #print urlencode(parts[0].replace(" ", ""))
            #FixME:如果传过来的uri不经过encode，可能会带来问题
            parameter = parts[0].replace(" ", "")

            if not parameter:
                continue

            """
            if conf.paramDel and conf.paramDel == '\n':
                parts[-1] = parts[-1].rstrip()
            """

        #if condition:
        testableParameters[parameter] = "=".join(parts[1:])

    return testableParameters

    """
    if place == PLACE.COOKIE:
        splitParams = parameters.split(conf.cookieDel or DEFAULT_COOKIE_DELIMITER)
    else:
        splitParams = parameters.split(conf.paramDel or DEFAULT_GET_POST_DELIMITER)

    for element in splitParams:
        element = re.sub(r"%s(.+?)%s" % (PARAMETER_AMP_MARKER, PARAMETER_SEMICOLON_MARKER), r"&\g<1>;", element)
        parts = element.split("=")

        if len(parts) >= 2:
            parameter = urldecode(parts[0].replace(" ", ""))

            if not parameter:
                continue

            if conf.paramDel and conf.paramDel == '\n':
                parts[-1] = parts[-1].rstrip()

            condition = not conf.testParameter
            condition |= conf.testParameter is not None and parameter in conf.testParameter
            condition |= place == PLACE.COOKIE and len(intersect((PLACE.COOKIE,), conf.testParameter, True)) > 0

            if condition:
                testableParameters[parameter] = "=".join(parts[1:])
                if not conf.multipleTargets and not (conf.csrfToken and parameter == conf.csrfToken):
                    _ = urldecode(testableParameters[parameter], convall=True)
                    if (_.endswith("'") and _.count("'") == 1
                      or re.search(r'\A9{3,}', _) or re.search(DUMMY_USER_INJECTION, _))\
                      and not parameter.upper().startswith(GOOGLE_ANALYTICS_COOKIE_PREFIX):
                        warnMsg = "it appears that you have provided tainted parameter values "
                        warnMsg += "('%s') with most probably leftover " % element
                        warnMsg += "chars/statements from manual SQL injection test(s). "
                        warnMsg += "Please, always use only valid parameter values "
                        warnMsg += "so sqlmap could be able to run properly"
                        logger.warn(warnMsg)

                        message = "are you really sure that you want to continue (sqlmap could have problems)? [y/N] "
                        test = readInput(message, default="N")
                        if test[0] not in ("y", "Y"):
                            raise SqlmapSilentQuitException
                    elif not _:
                        warnMsg = "provided value for parameter '%s' is empty. " % parameter
                        warnMsg += "Please, always use only valid parameter values "
                        warnMsg += "so sqlmap could be able to run properly"
                        logger.warn(warnMsg)

    if conf.testParameter and not testableParameters:
        paramStr = ", ".join(test for test in conf.testParameter)

        if len(conf.testParameter) > 1:
            warnMsg = "provided parameters '%s' " % paramStr
            warnMsg += "are not inside the %s" % place
            logger.warn(warnMsg)
        else:
            parameter = conf.testParameter[0]

            if not intersect(USER_AGENT_ALIASES + REFERER_ALIASES + HOST_ALIASES, parameter, True):
                debugMsg = "provided parameter '%s' " % paramStr
                debugMsg += "is not inside the %s" % place
                print(debugMsg)

    elif len(conf.testParameter) != len(testableParameters.keys()):
        for parameter in conf.testParameter:
            if parameter not in testableParameters:
                debugMsg = "provided parameter '%s' " % parameter
                debugMsg += "is not inside the %s" % place
                print(debugMsg)

    if testableParameters:
        for parameter, value in testableParameters.items():
            if value and not value.isdigit():
                for encoding in ("hex", "base64"):
                    try:
                        decoded = value.decode(encoding)
                        if len(decoded) > MIN_ENCODED_LEN_CHECK and all(_ in string.printable for _ in decoded):
                            warnMsg = "provided parameter '%s' " % parameter
                            warnMsg += "seems to be '%s' encoded" % encoding
                            logger.warn(warnMsg)
                            break
                    except:
                        pass
    """

def test(pageTemplate, page):
    seqMatcher = difflib.SequenceMatcher(None)
    seqMatcher.set_seq1(pageTemplate)
    page = removeDynamicContent(page)
    seqMatcher.set_seq1(removeDynamicContent(pageTemplate))

    pageLength = len(page)

    seq1, seq2 = None, None

    seq1 = seqMatcher.a
    seq2 = page


    if seq1 is None or seq2 is None:
            return None

    count = 0
    while count < min(len(seq1), len(seq2)):
        if seq1[count] == seq2[count]:
            count += 1
        else:
            break
    if count:
        seq1 = seq1[count:]
        seq2 = seq2[count:]

    while True:
        try:
            seqMatcher.set_seq1(seq1)
        except MemoryError:
            seq1 = seq1[:len(seq1) / 1024]
        else:
            break

    while True:
        try:
            seqMatcher.set_seq2(seq2)
        except MemoryError:
            seq2 = seq2[:len(seq2) / 1024]
        else:
            break

    ratio = round(seqMatcher.quick_ratio(), 3)

    if ratio > UPPER_RATIO_BOUND:
        print 1

def extractTextTagContent(page):
    """
    Returns list containing content from "textual" tags

    >>> extractTextTagContent(u'<html><head><title>Title</title></head><body><pre>foobar</pre><a href="#link">Link</a></body></html>')
    [u'Title', u'foobar']
    """

    page = page or ""
    if REFLECTED_VALUE_MARKER in page:
        page = re.sub(r"(?si)[^\s>]*%s[^\s<]*" % REFLECTED_VALUE_MARKER, "", page)
    return filter(None, (_.group('result').strip() for _ in re.finditer(TEXT_TAG_REGEX, page)))

def intersect(valueA, valueB, lowerCase=False):
    """
    Returns intersection of the array-ized values

    >>> intersect([1, 2, 3], set([1,3]))
    [1, 3]
    """

    retVal = []

    if valueA and valueB:
        valueA = arrayizeValue(valueA)
        valueB = arrayizeValue(valueB)

        if lowerCase:
            valueA = [val.lower() if isinstance(val, basestring) else val for val in valueA]
            valueB = [val.lower() if isinstance(val, basestring) else val for val in valueB]

        retVal = [val for val in valueA if val in valueB]

    return retVal

def arrayizeValue(value):
    """
    Makes a list out of value if it is not already a list or tuple itself

    >>> arrayizeValue(u'1')
    [u'1']
    """

    if not isListLike(value):
        value = [value]

    return value



class InjectionDict(AttribDict):
    def __init__(self):
        AttribDict.__init__(self)

        self.place = None
        self.parameter = None
        self.ptype = None
        self.prefix = None
        self.suffix = None
        self.clause = None

        # data is a dict with various stype, each which is a dict with
        # all the information specific for that stype
        self.data = AttribDict()

        # conf is a dict which stores current snapshot of important
        # options used during detection
        self.conf = AttribDict()

        self.dbms = None
        self.dbms_version = None
        self.os = None

def calculateDeltaSeconds(start):
    """
    Returns elapsed time from start till now

    >>> calculateDeltaSeconds(0) > 1151721660
    True
    """

    return time.time() - start

def stdev(values):
    """
    Computes standard deviation of a list of numbers.

    # Reference: http://www.goldb.org/corestats.html

    >>> "%.3f" % stdev([0.9, 0.9, 0.9, 1.0, 0.8, 0.9])
    '0.063'
    """

    if not values or len(values) < 2:
        return None
    else:
        avg = average(values)
        _ = 1.0 * sum(pow((_ or 0) - avg, 2) for _ in values)
        return sqrt(_ / (len(values) - 1))


def average(values):
    """
    Computes the arithmetic mean of a list of numbers.

    >>> "%.1f" % average([0.9, 0.9, 0.9, 1.0, 0.8, 0.9])
    '0.9'
    """

    return (1.0 * sum(values) / len(values)) if values else None


class Backend(object):
    @staticmethod
    def setDbms(dbms):
        dbms = aliasToDbmsEnum(dbms)

        if dbms is None:
            return None
        elif kb.dbms is None:
            kb.dbms = aliasToDbmsEnum(dbms)

        return kb.dbms

    @staticmethod
    def setVersion(version):
        if isinstance(version, six.string_types):
            dbmsVersion = [version]

        return dbmsVersion

    @staticmethod
    def getDbms():
        return aliasToDbmsEnum(kb.get("dbms"))

    # Get methods
    @staticmethod
    def getForcedDbms():
        return aliasToDbmsEnum(kb.get("forcedDbms"))

    @staticmethod
    def getIdentifiedDbms():
        """
        This functions is called to:

        1. Sort the tests, getSortedInjectionTests() - detection phase.
        2. Etc.
        """

        dbms = None

        if not kb:
            pass
        elif not kb.get("testMode") and conf.get("dbmsHandler") and getattr(conf.dbmsHandler, "_dbms", None):
            dbms = conf.dbmsHandler._dbms
        elif Backend.getForcedDbms() is not None:
            dbms = Backend.getForcedDbms()
        elif Backend.getDbms() is not None:
            dbms = Backend.getDbms()
        elif kb.get("injection") and kb.injection.dbms:
            dbms = unArrayizeValue(kb.injection.dbms)
        elif Backend.getErrorParsedDBMSes():
            dbms = unArrayizeValue(Backend.getErrorParsedDBMSes())
        elif conf.get("dbms"):
            dbms = conf.get("dbms")

        return aliasToDbmsEnum(dbms)

    @staticmethod
    def isDbms(dbms):
        return Backend.getIdentifiedDbms() == aliasToDbmsEnum(dbms)


def setCookie(cookie):
    cookie = "Cookie: " + cookie
    conf.default_header.append(cookie)


def isNullValue(value):
    """
    Returns whether the value contains explicit 'NULL' value

    >>> isNullValue(u'NULL')
    True
    >>> isNullValue(u'foobar')
    False
    """
    print hasattr(value, "upper") and value.upper() == 'NULL'
    return hasattr(value, "upper") and value.upper() == 'NULL'


def zeroDepthSearch(expression, value):
    """
    Searches occurrences of value inside expression at 0-depth level
    regarding the parentheses

    >>> _ = "SELECT (SELECT id FROM users WHERE 2>1) AS result FROM DUAL"; _[zeroDepthSearch(_, "FROM")[0]:]
    'FROM DUAL'
    """

    retVal = []

    depth = 0
    for index in xrange(len(expression)):
        if expression[index] == '(':
            depth += 1
        elif expression[index] == ')':
            depth -= 1
        elif depth == 0 and expression[index:index + len(value)] == value:
            retVal.append(index)

    return retVal


def splitFields(fields, delimiter=','):
    """
    Returns list of (0-depth) fields splitted by delimiter

    >>> splitFields('foo, bar, max(foo, bar)')
    ['foo', 'bar', 'max(foo,bar)']
    """

    fields = fields.replace("%s " % delimiter, delimiter)
    commas = [-1, len(fields)]
    commas.extend(zeroDepthSearch(fields, ','))
    commas = sorted(commas)

    return [fields[x + 1:y] for (x, y) in _zip(commas, commas[1:])]


def aliasToDbmsEnum(dbms):
    """
    Returns major DBMS name from a given alias

    >>> aliasToDbmsEnum('mssql')
    'Microsoft SQL Server'
    """

    retVal = None

    if dbms:
        for key, item in DBMS_DICT.items():
            if dbms.lower() in item[0] or dbms.lower() == key.lower():
                retVal = key
                break

    return retVal


def unArrayizeValue(value):
    """
    Makes a value out of iterable if it is a list or tuple itself

    >>> unArrayizeValue(['1'])
    '1'
    >>> unArrayizeValue(['1', '2'])
    '1'
    >>> unArrayizeValue([['a', 'b'], 'c'])
    'a'
    >>> unArrayizeValue(_ for _ in xrange(10))
    0
    """

    if isListLike(value):
        if not value:
            value = None
        elif len(value) == 1 and not isListLike(value[0]):
            value = value[0]
        else:
            value = [_ for _ in flattenValue(value) if _ is not None]
            value = value[0] if len(value) > 0 else None
    elif inspect.isgenerator(value):
        value = unArrayizeValue([_ for _ in value])

    return value

def filterStringValue(value, charRegex, replacement=""):
    """
    Returns string value consisting only of chars satisfying supplied
    regular expression (note: it has to be in form [...])

    >>> filterStringValue('wzydeadbeef0123#', r'[0-9a-f]')
    'deadbeef0123'
    """

    retVal = value

    if value:
        retVal = re.sub(charRegex.replace("[", "[^") if "[^" not in charRegex else charRegex.replace("[^", "["), replacement, value)

    return retVal


def removeReflectiveValues(content, payload, suppressWarning=False):
    """
    Neutralizes reflective values in a given content based on a payload
    (e.g. ..search.php?q=1 AND 1=2 --> "...searching for <b>1%20AND%201%3D2</b>..." --> "...searching for <b>__REFLECTED_VALUE__</b>...")
    """

    retVal = content

    try:
        if all((content, payload)) and isinstance(content, six.text_type) and kb.reflectiveMechanism and not kb.heuristicMode:
            def _(value):
                while 2 * REFLECTED_REPLACEMENT_REGEX in value:
                    value = value.replace(2 * REFLECTED_REPLACEMENT_REGEX, REFLECTED_REPLACEMENT_REGEX)
                return value

            payload = getUnicode(urldecode(payload.replace(PAYLOAD_DELIMITER, ""), convall=True))
            regex = _(filterStringValue(payload, r"[A-Za-z0-9]", encodeStringEscape(REFLECTED_REPLACEMENT_REGEX)))

            if regex != payload:
                if all(part.lower() in content.lower() for part in filterNone(regex.split(REFLECTED_REPLACEMENT_REGEX))[1:]):  # fast optimization check
                    parts = regex.split(REFLECTED_REPLACEMENT_REGEX)

                    # Note: naive approach
                    retVal = content.replace(payload, REFLECTED_VALUE_MARKER)
                    retVal = retVal.replace(re.sub(r"\A\w+", "", payload), REFLECTED_VALUE_MARKER)

                    if len(parts) > REFLECTED_MAX_REGEX_PARTS:  # preventing CPU hogs
                        regex = _("%s%s%s" % (REFLECTED_REPLACEMENT_REGEX.join(parts[:REFLECTED_MAX_REGEX_PARTS // 2]), REFLECTED_REPLACEMENT_REGEX, REFLECTED_REPLACEMENT_REGEX.join(parts[-REFLECTED_MAX_REGEX_PARTS // 2:])))

                    parts = filterNone(regex.split(REFLECTED_REPLACEMENT_REGEX))

                    if regex.startswith(REFLECTED_REPLACEMENT_REGEX):
                        regex = r"%s%s" % (REFLECTED_BORDER_REGEX, regex[len(REFLECTED_REPLACEMENT_REGEX):])
                    else:
                        regex = r"\b%s" % regex

                    if regex.endswith(REFLECTED_REPLACEMENT_REGEX):
                        regex = r"%s%s" % (regex[:-len(REFLECTED_REPLACEMENT_REGEX)], REFLECTED_BORDER_REGEX)
                    else:
                        regex = r"%s\b" % regex

                    _retVal = [retVal]

                    def _thread(regex):
                        try:
                            _retVal[0] = re.sub(r"(?i)%s" % regex, REFLECTED_VALUE_MARKER, _retVal[0])

                            if len(parts) > 2:
                                regex = REFLECTED_REPLACEMENT_REGEX.join(parts[1:])
                                _retVal[0] = re.sub(r"(?i)\b%s\b" % regex, REFLECTED_VALUE_MARKER, _retVal[0])
                        except KeyboardInterrupt:
                            raise
                        except:
                            pass

                    thread = threading.Thread(target=_thread, args=(regex,))
                    thread.daemon = True
                    thread.start()
                    thread.join(REFLECTED_REPLACEMENT_TIMEOUT)

                    if thread.isAlive():
                        kb.reflectiveMechanism = False
                        retVal = content
                        if not suppressWarning:
                            debugMsg = "turning off reflection removal mechanism (because of timeouts)"
                            print(debugMsg)
                    else:
                        retVal = _retVal[0]

                if retVal != content:
                    kb.reflectiveCounters[REFLECTIVE_COUNTER.HIT] += 1
                    if not suppressWarning:
                        warnMsg = "reflective value(s) found and filtering out"
                        singleTimeWarnMessage(warnMsg)

                    if re.search(r"(?i)FRAME[^>]+src=[^>]*%s" % REFLECTED_VALUE_MARKER, retVal):
                        warnMsg = "frames detected containing attacked parameter values. Please be sure to "
                        warnMsg += "test those separately in case that attack on this page fails"
                        singleTimeWarnMessage(warnMsg)

                elif not kb.testMode and not kb.reflectiveCounters[REFLECTIVE_COUNTER.HIT]:
                    kb.reflectiveCounters[REFLECTIVE_COUNTER.MISS] += 1
                    if kb.reflectiveCounters[REFLECTIVE_COUNTER.MISS] > REFLECTIVE_MISS_THRESHOLD:
                        kb.reflectiveMechanism = False
                        if not suppressWarning:
                            debugMsg = "turning off reflection removal mechanism (for optimization purposes)"
                            print(debugMsg)
    except MemoryError:
        kb.reflectiveMechanism = False
        if not suppressWarning:
            debugMsg = "turning off reflection removal mechanism (because of low memory issues)"
            print(debugMsg)

    return retVal