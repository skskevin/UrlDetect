#from core.utils.enums import PLACEMETHOD
import re
import urlparse
from common import paramToDict
from common import urlencode
from lib.utils.common import randomInt, randomStr, getUnicode
from lib.utils.unescaper import unescaper
from lib.utils.enums import PLACE, PAYLOAD, SLEEP_TIME_MARKER, SINGLE_QUOTE_MARKER
from lib.utils.common import extractRegexResult
from lib.config import conf


PAYLOAD_DELIMITER = "__PAYLOAD_DELIMITER__"
BOUNDARY_BACKSLASH_MARKER = "__BACKSLASH__"




class Agent(object):

    def addPayloadDelimiters(self, value):
        """
        Adds payload delimiters around the input string
        """
        return value
        #return "%s%s%s" % (PAYLOAD_DELIMITER, value, PAYLOAD_DELIMITER) if
        #value else value

    def extractPayload(self, value):
        """
        Extracts payload from inside of the input string
        """

        _ = re.escape(PAYLOAD_DELIMITER)

        return extractRegexResult("(?s)%s(?P<result>.*?)%s" % (_, _), value)

    def cleanupPayload(self, payload, origValue=None):
        if payload is None:
            return

        _ = (('[DELIMITER_START]', 'qzkzq'), ('[DELIMITER_STOP]', 'qpkpq'), ('[AT_REPLACE]', 'qtq'), ('[SPACE_REPLACE]', 'qiq'), ('[DOLLAR_REPLACE]', 'qvq'), ('[HASH_REPLACE]', 'qiq'))

        payload = reduce(lambda x, y: x.replace(y[0], y[1]), _, payload)

        for _ in set(re.findall(r"\[RANDNUM(?:\d+)?\]", payload, re.I)):
            payload = payload.replace(_, str(randomInt()))

        for _ in set(re.findall(r"\[RANDSTR(?:\d+)?\]", payload, re.I)):
            payload = payload.replace(_, randomStr())

        if origValue is not None:
            payload = payload.replace("[ORIGVALUE]", origValue if origValue.isdigit() else unescaper.escape("'%s'" % origValue))

        if "[INFERENCE]" in payload:
            if Backend.getIdentifiedDbms() is not None:
                inference = queries[Backend.getIdentifiedDbms()].inference

                if "dbms_version" in inference:
                    if isDBMSVersionAtLeast(inference.dbms_version):
                        inferenceQuery = inference.query
                    else:
                        inferenceQuery = inference.query2
                else:
                    inferenceQuery = inference.query

                payload = payload.replace("[INFERENCE]", inferenceQuery)
            elif not kb.testMode:
                errMsg = "invalid usage of inference payload without "
                errMsg += "knowledge of underlying DBMS"
                raise SqlmapNoneDataException(errMsg)

        return payload


    def prefixQuery(self, expression, prefix=None, where=None, clause=None):
        """
        This method defines how the input expression has to be escaped
        to perform the injection depending on the injection type
        identified as valid
        """


        if expression is None:
            return None

        expression = self.cleanupPayload(expression)
        expression = unescaper.escape(expression)
        query = prefix or ""
        if not (expression and expression[0] == ';') and not (query and query[-1] in ('(', ')') and expression and expression[0] in ('(', ')')) and not (query and query[-1] == '('):
                query += " "
        query = "%s%s" % ((query or ""), expression)

        return query

    def suffixQuery(self, expression, comment=None, suffix=None, where=None):
        """
        This method appends the DBMS comment to the
        SQL injection request
        """

        if expression is None:
            return None

        expression = self.cleanupPayload(expression)

        if comment is not None:
            expression += comment

        if suffix and not comment:
            expression += suffix

        return re.sub(r"(?s);\W*;", ";", expression)

    
    def adjustLateValues(self, payload):
            """
            Returns payload with a replaced late tags (e.g. SLEEPTIME)
            """

            if payload:
                payload = payload.replace(SLEEP_TIME_MARKER, str(conf.timeSec))
                payload = payload.replace(SINGLE_QUOTE_MARKER, "'")

                for _ in set(re.findall(r"\[RANDNUM(?:\d+)?\]", payload, re.I)):
                    payload = payload.replace(_, str(randomInt()))

                for _ in set(re.findall(r"\[RANDSTR(?:\d+)?\]", payload, re.I)):
                    payload = payload.replace(_, randomStr())

            return payload

    def getComment(self, request):
        """
        Returns comment form for the given request
        """

        return request.comment if "comment" in request else ""


    def payload_t(self, paramDict, parameters=None, place=None, parameter=None, value=None, newValue=None, where=None):
        """
        This method replaces the affected parameter with the SQL
        injection statement to request
        """

        retVal = ""
        paramString = parameters[place]
        paramDict = paramDict[place]
        origValue = getUnicode(paramDict[parameter])

        #如果参数值为空则生成个值
        if value is None:
            if where == PAYLOAD.WHERE.ORIGINAL:
                value = origValue
            elif where == PAYLOAD.WHERE.NEGATIVE:
                # if conf.invalidLogical:
                #     match = re.search(r'\A[^ ]+', newValue)
                #     newValue = newValue[len(match.group() if match else ""):]
                #     _ = randomInt(2)
                #     value = "%s%s AND %s=%s" % (origValue, match.group() if match else "", _, _ + 1)
                # elif conf.invalidBignum:
                #     value = randomInt(6)
                # elif conf.invalidString:
                #     value = randomStr(6)
                # else:
                if newValue.startswith("-"):
                    value = ""
                else:
                    value = "-%s" % randomInt()
            elif where == PAYLOAD.WHERE.REPLACE:
                value = ""
            else:
                value = origValue

            newValue = "%s%s" % (value, newValue)

        newValue = self.cleanupPayload(newValue, origValue)

        #支持修改http中各种请求的参数
        if place in (PLACE.URI, PLACE.CUSTOM_POST, PLACE.CUSTOM_HEADER):
            pass
        elif place in (PLACE.USER_AGENT, PLACE.REFERER, PLACE.HOST):
            pass
        else:
            def _(pattern, repl, string):
                retVal = string
                match = None
                for match in re.finditer(pattern, string):
                    pass

                if match:
                    while True:
                        _ = re.search(r"\\g<([^>]+)>", repl)
                        if _:
                            try:
                                repl = repl.replace(_.group(0), match.group(int(_.group(1)) if _.group(1).isdigit() else _.group(1)))
                            except IndexError:
                                break
                        else:
                            break
                    retVal = string[:match.start()] + repl + string[match.end():]
                return retVal

            if origValue:
                regex = r"(\A|\b)%s=%s%s" % (re.escape(parameter), re.escape(origValue), r"(\Z|\b)" if origValue[-1].isalnum() else "")
                retVal = _(regex, "%s=%s" % (parameter, self.addPayloadDelimiters(newValue.replace("\\", "\\\\"))), paramString)
            else:
                retVal = _(r"(\A|\b)%s=%s(\Z|%s|%s|\s)" % (re.escape(parameter), re.escape(origValue), DEFAULT_GET_POST_DELIMITER, DEFAULT_COOKIE_DELIMITER), "%s=%s\g<2>" % (parameter, self.addPayloadDelimiters(newValue.replace("\\", "\\\\"))), paramString)

            if retVal == paramString and urlencode(parameter) != parameter:
                pass
                retVal = _(r"(\A|\b)%s=%s" % (re.escape(urlencode(parameter)), re.escape(origValue)), "%s=%s" % (urlencode(parameter), self.addPayloadDelimiters(newValue.replace("\\", "\\\\"))), paramString)


        if retVal:
            retVal = retVal.replace(BOUNDARY_BACKSLASH_MARKER, '\\')

        return retVal




    def payload(self, place=None, parameter=None, value=None, newValue=None, where=None, addValue=None):

        """
        This method replaces the affected parameter with the SQL
        injection statement to request
        """
      
        retVal = ""
        paramString = place['paramstring']
        paramDict = place['paramdict']
        origValue = paramDict[parameter]#getUnicode(paramDict[parameter])
        
        randstr = ""

        if addValue is not None:
            value = origValue
            newValue = "%s%s" % (value, addValue)
            newValue = urlencode(newValue, '%', False, 'GET' != 'URI')
        else:
            if value is None:
                if all(c in "0123456789.+-" for c in parameter):
                    randstr = str(randomInt())
                else:
                    randstr = randomStr()
            
                return randstr

        #    """
        #    if where == PAYLOAD.WHERE.ORIGINAL:
        #        value = origValue
        #    elif where == PAYLOAD.WHERE.NEGATIVE:
        #        if conf.invalidLogical:
        #            match = re.search(r'\A[^ ]+', newValue)
        #            newValue = newValue[len(match.group() if match else ""):]
        #            _ = randomInt(2)
        #            value = "%s%s AND %s=%s" % (origValue, match.group() if
        #            match else "", _, _ + 1)
        #        elif conf.invalidBignum:
        #            value = randomInt(6)
        #        elif conf.invalidString:
        #            value = randomStr(6)
        #        else:
        #            if newValue.startswith("-"):
        #                value = ""
        #            else:
        #                value = "-%s" % randomInt()
        #    """
        

        if False:
            pass
        else:
            def _(pattern, repl, string):
                retVal = string
                match = None
                for match in re.finditer(pattern, string):
                    pass

                if match:
                    while True:
                        _ = re.search(r"\\g<([^>]+)>", repl)
                        if _:
                            try:
                                repl = repl.replace(_.group(0), match.group(int(_.group(1)) if _.group(1).isdigit() else _.group(1)))
                            except IndexError:
                                break
                        else:
                            break
                    retVal = string[:match.start()] + repl + string[match.end():]
                return retVal

            if origValue:
                regex = r"(\A|\b)%s=%s%s" % (re.escape(parameter), re.escape(origValue), r"(\Z|\b)" if origValue[-1].isalnum() else "")
                retVal = _(regex, "%s=%s" % (parameter, self.addPayloadDelimiters(newValue.replace("\\", "\\\\"))), paramString)

            
            """
            else:
                retVal = _(r"(\A|\b)%s=%s(\Z|%s|%s|\s)" % (re.escape(parameter), re.escape(origValue), DEFAULT_GET_POST_DELIMITER, DEFAULT_COOKIE_DELIMITER), "%s=%s\g<2>" % (parameter, self.addPayloadDelimiters(newValue.replace("\\", "\\\\"))), paramString)

            if retVal == paramString and urlencode(parameter) != parameter:
                retVal = _(r"(\A|\b)%s=%s" % (re.escape(urlencode(parameter)), re.escape(origValue)), "%s=%s" % (urlencode(parameter), self.addPayloadDelimiters(newValue.replace("\\", "\\\\"))), paramString)
            """

        if retVal:
            retVal = retVal.replace(BOUNDARY_BACKSLASH_MARKER, '\\')

        return retVal
       
agent = Agent()




