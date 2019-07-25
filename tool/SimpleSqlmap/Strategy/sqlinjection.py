from core.utils.common import randomStr, parseXmlFile, readCachedFileContent, urlencode, getUnicode, paramToDict_t, urldecode, extractTextTagContent, InjectionDict, intersect
from core.request.queryPage import queryPage
from core.request.queryPage import proxyqueryPage
import urlparse

from core.utils.checks import checkDynParam, checkDynParam_t, HTTPCheck
from core.utils.common import paramToDict
from core.utils.Agent import agent
from xml.sax.handler import ContentHandler
import re
from xml.etree import ElementTree as et
from core.utils.common import cleanupVals
from core.utils.common import AttribDict
from core.utils.Agent import Agent
import os
import copy
from core.utils.enums import PLACE, SORT_ORDER, CUSTOM_INJECTION_MARK_CHAR, DEFAULT_GET_POST_DELIMITER, URI_QUESTION_MARKER, HEURISTIC_CHECK_ALPHABET, TECHNIQUE, WHERE, PAYLOAD





dbms = None
ErrorPage = None
tests = []
boundaries = []
parameters = {}
uri = None

file_path = "/Users/dongchuan/work/cmcm/python/SimpleSqlmap/xml/payloads"
xmlfile = "/Users/dongchuan/work/cmcm/python/SimpleSqlmap/xml/errors.xml"
boundaries_xml = "/Users/dongchuan/work/cmcm/python/SimpleSqlmap/xml/boundaries.xml"




class HTMLHandler(ContentHandler):
    """
    This class defines methods to parse the input HTML page to
    fingerprint the back-end database management system
    """

    def __init__(self, page):
        ContentHandler.__init__(self)

        self._dbms = None
        self._page = page
        self.dbms = None

    def _markAsErrorPage(self):
        global ErrorPage

        ErrorPage = self._page

    def startElement(self, name, attrs):
        global dbms

        if name == "dbms":
            self._dbms = attrs.get("value")

        elif name == "error":
            if re.search(attrs.get("regexp"), self._page, re.I):
                self.dbms = self._dbms
                dbms = self.dbms
                self._markAsErrorPage()



def Init():
    readCachedFileContent(xmlfile)

    payloadFiles = os.listdir(file_path)
    for payloadFile in payloadFiles:
        payloadFilePath = os.path.join(file_path, payloadFile)
        # print payloadFilePath

        try:
            doc = et.parse(payloadFilePath)
        except Exception, ex:
           pass

        root = doc.getroot()
        parseXmlNode(root)
    try:
        boundaries_doc = et.parse(boundaries_xml)
    except Exception, ex:
        pass
    boundaries_root = boundaries_doc.getroot()
    parseXmlNode(boundaries_root)

def getSortedInjectionTests():
    global boundaries
    global tests
    global dbms
    """
    Returns prioritized test list by eventually detected DBMS from error
    messages
    """
    retVal = copy.deepcopy(tests)

    def priorityFunction(test):
        retVal = SORT_ORDER.FIRST

        if test.stype == TECHNIQUE.UNION:
            retVal = SORT_ORDER.LAST

        elif 'details' in test and 'dbms' in test.details:
            #print type(test)
            #if intersect(test.details.dbms, Backend.getIdentifiedDbms()):
            if test.details.dbms == dbms:
                retVal = SORT_ORDER.SECOND
            else:
                retVal = SORT_ORDER.THIRD

        return retVal

    if dbms:
        retVal = sorted(retVal, key=priorityFunction)

    return retVal

def geturl(payload):
    if(payload):
        if '?' in uri:
            url = "%s%s%s" % (uri, DEFAULT_GET_POST_DELIMITER, get)
        else:
            url = "%s?%s" % (uri, payload)
    return url


def checkSqlInjection(place, parameter, value, paramDict, parameters, url_test):

    global tests
    global boundaries


    injection = InjectionDict()
    tests_check = getSortedInjectionTests()
    seenPayload = set()
    # dbms = 'MySQL'
    extendTests = dbms
    reduceTests = dbms

    while tests:
        test = tests.pop(0)
        title = test.title
        clause = test.clause
        stype = test.stype
        # print title
        


        if stype == PAYLOAD.TECHNIQUE.UNION:
            if "[CHAR]" in title:
                continue

            elif "[RANDNUM]" in title or "(NULL)" in title:
                    title = title.replace("[RANDNUM]", "random number")

            if test.request.columns == "[COLSTART]-[COLSTOP]":
                continue

            match = re.search(r"(\d+)-(\d+)", test.request.columns)
            if injection.data and match:
                lower, upper = int(match.group(1)), int(match.group(2))
                for _ in (lower, upper):
                    if _ > 1:
                        unionExtended = True
                        test.request.columns = re.sub(r"\b%d\b" % _, str(2 * _), test.request.columns)
                        title = re.sub(r"\b%d\b" % _, str(2 * _), title)
                        test.title = re.sub(r"\b%d\b" % _, str(2 * _), test.title)


        if injection.data and stype in injection.data:
            continue


        # Parse DBMS-specific payloads' details
        if "details" in test and "dbms" in test.details:
            payloadDbms = test.details.dbms
        else:
            payloadDbms = None


        if payloadDbms is not None:

            if reduceTests and not intersect(payloadDbms, reduceTests, True):
                continue


        comment = agent.getComment(test.request) if len(boundaries) > 1 else None
        fstPayload = agent.cleanupPayload(test.request.payload, origValue=value)

        if value.isdigit():
            boundaries = sorted(copy.deepcopy(boundaries), key=lambda x: any(_ in (x.prefix or "") or _ in (x.suffix or "") for _ in ('"', '\'')))

        for boundary in boundaries:
            injectable = False

            if boundary.level > 1:
                continue

            clauseMatch = False

            for clauseTest in test.clause:
                if clauseTest in boundary.clause:
                    clauseMatch = True
                    break

            if test.clause != [0] and boundary.clause != [0] and not clauseMatch:
                continue

            whereMatch = False

            for where in test.where:
                if where in boundary.where:
                    whereMatch = True
                    break

            if not whereMatch:
                continue

                # Parse boundary's <prefix>, <suffix> and <ptype>
            prefix = boundary.prefix if boundary.prefix else ""
            suffix = boundary.suffix if boundary.suffix else ""
            ptype = boundary.ptype


            condBound = (injection.prefix is not None and injection.suffix is not None)
            condBound &= (injection.prefix != prefix or injection.suffix != suffix)
            condType = injection.ptype is not None and injection.ptype != ptype


            if stype != PAYLOAD.TECHNIQUE.QUERY and (condBound or condType):
                    continue

            for where in test.where:
                templatePayload = None
                vector = None

                # Threat the parameter original value according to the
                # test's <where> tag
                if where == WHERE.ORIGINAL:
                    origValue = value

                    templatePayload = None

                if fstPayload:
                    boundPayload = agent.prefixQuery(fstPayload, prefix, where, clause)
                    boundPayload = agent.suffixQuery(boundPayload, comment, suffix, where)
                    reqPayload = agent.payload_t(paramDict, parameters, place, parameter, newValue=boundPayload, where=where)
                    if reqPayload:
                        if reqPayload in seenPayload:
                            continue
                        else:
                            seenPayload.add(reqPayload)
                else:
                    reqPayload = None

                for method, check in test.response.items():
                    check = agent.cleanupPayload(check, origValue=value if place not in (PLACE.URI, PLACE.CUSTOM_POST, PLACE.CUSTOM_HEADER) else None)

                    if method == PAYLOAD.METHOD.COMPARISON:
                        def genCmpPayload():
                            sndPayload = agent.cleanupPayload(test.response.comparison, origValue=value if place not in (PLACE.URI, PLACE.CUSTOM_POST, PLACE.CUSTOM_HEADER) else None)

                            # Forge response payload by prepending with
                            # boundary's prefix and appending the
                            # boundary's
                            # suffix to the test's ' <payload><comment> '
                            # string
                            boundPayload = agent.prefixQuery(sndPayload, prefix, where, clause)
                            boundPayload = agent.suffixQuery(boundPayload, comment, suffix, where)
                            cmpPayload = agent.payload_t(paramDict, parameters, place, parameter, newValue=boundPayload, where=where)

                            return cmpPayload
                        
                        url = geturl(genCmpPayload())
                        falseResponse = proxyqueryPage(url)
                        falsePage = falseResponse.getdata()

                        url = geturl(reqPayload)
                        trueResponse = proxyqueryPage(url)
                        truePage = trueResponse.getdata()
                        trueResult = url_test.comparison(truePage)

                        if trueResult and not(truePage == falsePage):
                            url = geturl(genCmpPayload())
                            falseResponse = proxyqueryPage(url)
                            falsePage = falseResponse.getdata()
                            falseResult = url_test.comparison(falsePage)
                            if not falseResult:
                                injectable = True

                        if not injectable:
                            trueSet = set(extractTextTagContent(truePage))
                            falseSet = set(extractTextTagContent(falsePage))
                            candidates = filter(None, (_.strip() if _.strip() in (url_test.firstPage or "") and _.strip() not in falsePage and _.strip() else None for _ in (trueSet - falseSet)))


                            if candidates:
                                injectable = True


                    elif method == PAYLOAD.METHOD.UNION:
                        pass


                if injectable is True:
                    if injection.place is None or injection.parameter is None:
                        if place in (PLACE.USER_AGENT, PLACE.REFERER, PLACE.HOST):
                                injection.parameter = place
                        else:
                                injection.parameter = parameter

                        injection.place = place
                        injection.ptype = ptype
                        injection.prefix = prefix
                        injection.suffix = suffix
                        injection.clause = clause


                        if hasattr(test, "details"):
                            for dKey, dValue in test.details.items():
                                if dKey == "dbms":
                                    injection.dbms = dValue

                                elif dKey == "dbms_version" and injection.dbms_version is None and not conf.testFilter:
                                    injection.dbms_version = Backend.setVersion(dValue)

                                elif dKey == "os" and injection.os is None:
                                    injection.os = Backend.setOs(dValue)


                        if vector is None and "vector" in test and test.vector is not None:
                            vector = test.vector

                        injection.data[stype] = AttribDict()
                        injection.data[stype].title = title
                        injection.data[stype].payload = reqPayload
                        injection.data[stype].where = where
                        injection.data[stype].vector = vector
                        injection.data[stype].comment = comment
                        injection.data[stype].templatePayload = templatePayload

                        break


            # print title
            if injectable is True:
                # break
                print injectable,injection
                # break
                    

                    



                                 
def heuristicCheckSqlInjection(place, parameter, paramDict, parameters):
    global ErrorPage
    global dbms

    origValue = paramDict[place][parameter]

    randStr = ""
    while '\'' not in randStr:
        randStr = randomStr(length=10, alphabet=HEURISTIC_CHECK_ALPHABET)

    payload = agent.payload_t(paramDict, parameters, place, parameter, newValue=randStr)
    #payload = agent.payload(place, key, addValue=randStr)
    url = geturl(payload)
    response = proxyqueryPage(url)
    page = response.getdata()

    handler = HTMLHandler(page)

    parseXmlFile(xmlfile, handler)

        
    if ErrorPage:
        return True
    else:
        return False

def parseTargetUrl(url):
    global parameters
    global uri


    parseTargetUrl = url

    if not re.search("^http[s]*://", url, re.I) and \
            not re.search("^ws[s]*://", url, re.I):
        if ":443/" in conf.url:
            url = "https://" + url
        else:
            url = "http://" + url
    try:
        urlSplit = urlparse.urlsplit(url)
    except ValueError, ex:
        pass
    hostnamePort = urlSplit.netloc.split(":") if not re.search("\[.+\]", urlSplit.netloc) else filter(None, (re.search("\[.+\]", urlSplit.netloc).group(0), re.search("\](:(?P<port>\d+))?", urlSplit.netloc).group("port")))
    scheme = urlSplit.scheme.strip().lower()
    path = urlSplit.path.strip()
    hostname = hostnamePort[0].strip()

    ipv6 = hostname != hostname.strip("[]")
    hostname = hostname.strip("[]").replace(CUSTOM_INJECTION_MARK_CHAR, "")

    if len(hostnamePort) == 2:
        try:
            port = int(hostnamePort[1])
        except:
            errMsg = "invalid target URL"
            raise SqlmapSyntaxException(errMsg)
    elif scheme == "https":
        port = 443
    else:
        port = 80
    if urlSplit.query:
        parameters[PLACE.GET] = urldecode(urlSplit.query) if urlSplit.query and urlencode(DEFAULT_GET_POST_DELIMITER, None) not in urlSplit.query else urlSplit.query

    uri = getUnicode("%s://%s:%d%s" % (scheme, ("[%s]" % hostname) if ipv6 else hostname, port, path))
    uri = uri.replace(URI_QUESTION_MARKER, '?')

def checkInjection(url):
    paramDict = {}

    #检测网页稳定性
    url_test = HTTPCheck(url)

    if(url_test.checkConnection()): #检测构造的探测自定义404地址是否能访问
        pass
    else:
        output = open('Error.txt', 'a') 
        output.write(url + '  not conn\n')
        output.close()
        return    #检测到如果连接出现问题则跳过

    if(url_test.checkStability()):  #检测url稳定性，并且找出动态内容
        pass
    else:
        output = open('Error.txt', 'a') 
        output.write(url + '  not Stability\n')
        output.close()
        return



    #解析所有参数以及GET请求方式
    parseTargetUrl(url)
    parameters_s = parameters[PLACE.GET]
    paramDicts = paramToDict_t(PLACE.GET, parameters_s)
    if paramDicts:
        paramDict[PLACE.GET] = paramDicts

    output = open('DynParam_test.txt', 'a') 
    output.write('\n' + url + ':::\n')
    output.close()

    #尝试所有GET参数是否是动态参数
    parameters_c = parameters.keys()
    for place in parameters_c:
         for parameter, value in paramDicts.items():
             check = checkDynParam_t(place, url_test, uri, paramDict, parameters, parameter, value)
             output = open('DynParam_test.txt', 'a') 
             output.write('Parameter key={0}, value={1}, check={2}\n'.format(parameter,value,check))
             output.close()
             print 'Parameter key={0}, value={1}, check={2}'.format(parameter,value,check) 

             if check:
                checkhh = heuristicCheckSqlInjection(place, parameter, paramDict, parameters)
                print checkhh
                injection = checkSqlInjection(place, parameter, value, paramDict, parameters, url_test)
                print injection
         

    #place = {}
    #if url.startswith("http://") or url.startswith("https://"):
       

    #    place['uri'] = url

    #    paramters = urlparse(url).query

    #    if not paramters:
    #        return
    #    else:
    #        place['paramstring'] = paramters

    #        paramDict = dict()

    #        paramDict = paramToDict(place['paramstring'])

    #        place['paramdict'] = paramDict

    #        for (key, value) in paramDict.items():
    #            #test
    #            checkDynParam_t(place, key, value)
    #            if not value:
    #                pass
    #                #print 'Empty Parameter Value, key={0} value= '.format(key)
    #            elif checkDynParam(place, key, value):
    #                pass
    #                #print 'Static Parameter key={0}, value={1}'.format(key,
    #                #value)
    #            else:
    #                heuristicCheckSqlInjection(place, paramters, key)

    #                checkSqlInjection(place, key, value)
                    
                    