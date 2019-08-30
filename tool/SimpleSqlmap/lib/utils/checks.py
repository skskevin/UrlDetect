import re
import socket
import time
import difflib
from difflib import SequenceMatcher
from lib.utils.Agent import agent
from lib.utils.urlparse import urlparse
from lib.request.queryPage import queryPage, proxyqueryPage
from lib.utils.common import randomInt, randomStr, getUnicode, stdev, average, calculateDeltaSeconds
from lib.utils.enums import PLACE,TIME_STDEV_COEFF,MIN_TIME_RESPONSES,MAX_TIME_RESPONSES
from lib.utils.enums import PAYLOAD_DELIMITER, MIN_VALID_DELAYED_RESPONSE
from lib.config import kb

DYNAMICITY_MARK_LENGTH = 8
UPPER_RATIO_BOUND = 0.983
LOWER_RATIO_BOUND = 0.02
DIFF_TOLERANCE = 0.05
UPPER_RATIO_BOUND_DYN = 0.999


_UNKNOWN = 'UNKNOWN'

def checkPageStability(firstPage, secondPage):
    try:
        pageCodeStable = (firstPage.getstatus() == secondPage.getstatus())
        if(pageCodeStable == False):
            return False
        pageStable = (firstPage.getdata() == secondPage.getdata())
        if pageStable:
            return True
        else:
            seqMatcher = difflib.SequenceMatcher(None)
            seqMatcher.set_seq1(firstPage.getdata())
            seqMatcher.set_seq2(secondPage.getdata())
            if seqMatcher.quick_ratio() <= UPPER_RATIO_BOUND:
                return False
            else:
                return True

    except:
        return False   

def checkComparison(firstPage, secondPage):
        seqMatcher = difflib.SequenceMatcher(None)
        seqMatcher.set_seq1(firstPage)

        pageLength = len(secondPage)

        seq1, seq2 = None, None

        seq1 = seqMatcher.a
        seq2 = secondPage


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
            return True
        else:
            return False

def diffRatio(pageA, pageB):
        seqMatcher = difflib.SequenceMatcher(None)
        seqMatcher.set_seq1(pageA)

        seq1, seq2 = None, None

        seq1 = seqMatcher.a
        seq2 = pageB


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
                seq1 = seq1[:len(seq1) / 2048]
            else:
                break

        while True:
            try:
                seqMatcher.set_seq2(seq2)
            except MemoryError:
                seq2 = seq2[:len(seq2) / 2048]
            else:
                break

        ratio = round(seqMatcher.quick_ratio(), 3)
        
        return ratio
 


def checkDynParam_t(place, url_test, uri, paramDict, parameters, parameter, value):
    dynResult = None
    randInt = randomInt()
    try:
        payload = agent.payload_t(paramDict, parameters, place, parameter, value, getUnicode(randInt))
        if(payload):
            url = "%s?%s" % (uri, payload)
        firstreponse = proxyqueryPage(url)
        dynResult = url_test.comparison(firstreponse.getdata())


        if not dynResult:
            #生成随机数  拼接成url 尝试两个不同的随机匹配结果
            randInt = randomInt()
            payload = agent.payload_t(paramDict, parameters, place, parameter, value, getUnicode(randInt))
            if(payload):
                url = "%s?%s" % (uri, payload)
            secondreponse  = proxyqueryPage(url)
            dynResult = url_test.comparison(secondreponse.getdata())
    except Exception as ex:
        print ex

    result = None if dynResult is None else not dynResult

    return result


#检测动态参数
def checkDynParam(place, parameter, value):
    """
    This function checks if the URL parameter is dynamic. If it is
    dynamic, the content of the page differs, otherwise the
    dynamicity might depend on another parameter.

    place
    """

    #if kb.redirectChoice:
    #    return None

    paramString = place['paramstring']

    #dynResult = None
    #randInt = randomInt()

    #infoMsg = "testing if %s parameter '%s' is dynamic" %
    #(str(type(paramType)), parameter)
    #logger.info(infoMsg)

    payload = ""
    randstr = ""

    length = len(value)

    try:
        #FixME:这个可以优化掉
        response = proxyqueryPage(place['uri'])

        httpCode = response.getstatus()
        page = response.getdata()

        if all(c in "0123456789.+-" for c in value):
            randstr = str(randomInt(length=length))
        else:
            randstr = randomStr(length=length)
        
        payload = agent.payload(place, parameter, value, randstr) 

        url = place['uri'].replace(paramString, payload)

        reponse = proxyqueryPage(url)

        firstPage = reponse.getdata()
        firstCode = reponse.getstatus()

        #second Page
        if all(c in "0123456789.+-" for c in value):
            randstr = str(randomInt(length=length))
        else:
            randstr = randomStr(length=length)
        
        payload = agent.payload(place, parameter, '', randstr) 
               
        url = place['uri'].replace(paramString, payload)
        reponse = queryPage(url)

        secondPage = reponse.getdata()
        secondCode = reponse.getstatus()

        ratio1 = diffRatio(page, firstPage)
        ratio2 = diffRatio(page, secondPage)

        if ratio1 > UPPER_RATIO_BOUND_DYN and ratio2 > UPPER_RATIO_BOUND_DYN:
            if secondCode == firstCode and httpCode == firstCode:
                if diffRatio(firstPage, secondPage) > UPPER_RATIO_BOUND:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    except:
        print 'Excepiton occurred url:{0}'.format(place['uri'].replace(paramString, payload))
        return False


class HTTPCheck:
     def __init__(self, url_str):
        self.firstCode = _UNKNOWN
        self.originalPageTime = _UNKNOWN
        self.firstPage = _UNKNOWN
        self.secondPage = _UNKNOWN
        self.url_str = url_str
        self.dynamicMarkings = []
        
     def checkConnection(self):
        try:
            urlSplit = urlparse(self.url_str)
            socket.getaddrinfo(urlSplit.hostname, None)
        except Exception, e:
            print e
            return False
        try:
            self.originalPageTime = time.time()
            h_response = queryPage(self.url_str, noteResponseTime=False)
            self.firstPage = h_response.getdata()
            kb.pageTemplate = h_response.getdata()
            self.firstCode = h_response.getstatus()
            return True
        except Exception, e:
            print e
            return False

     def checkPageStability(self,page,pagecode):
        try:
            self.secondPage = page

            pageCodeStable = (self.firstCode == pagecode)
            if(pageCodeStable == False):
                return False


            pageStable = (self.firstPage == self.secondPage)
            if pageStable:
                if self.firstPage:
                    return True
                else:
                    return True
            else:
                self.checkDynamicContent()
                return True
        except:
            return False

     def checkStability(self):
        delay = 1 - (time.time() - (self.originalPageTime or 0))
        delay = max(0, min(1, delay))
        time.sleep(delay)
        try:
            secondResponse = queryPage(self.url_str)
            self.secondPage = secondResponse.getdata()

            pageCodeStable = (self.firstCode == secondResponse.getstatus())
            if(pageCodeStable == False):
                return False


            pageStable = (self.firstPage == self.secondPage)
            if pageStable:
                if self.firstPage:
                    return True
                else:
                    return True
            else:
                self.checkDynamicContent()
                return True
        except:
            return False

     def checkDynamicContent(self):
        seqMatcher = difflib.SequenceMatcher(None)
        seqMatcher.set_seq1(self.firstPage)
        seqMatcher.set_seq2(self.secondPage)
        if seqMatcher.quick_ratio() <= UPPER_RATIO_BOUND:
            self.findDynamicContent()

     def findDynamicContent(self):
        """
        This function checks if the provided pages have dynamic content. If they
        are dynamic, proper markings will be made
        """
        if not self.firstPage or not self.secondPage:
            return
        blocks = SequenceMatcher(None, self.firstPage, self.secondPage).get_matching_blocks()
        self.dynamicMarkings = []
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
                prefix = self.firstPage[blocks[i][0]:blocks[i][0] + blocks[i][2]] if blocks[i] else None
                suffix = self.firstPage[blocks[i + 1][0]:blocks[i + 1][0] + blocks[i + 1][2]] if blocks[i + 1] else None


                if prefix is None and blocks[i + 1][0] == 0:
                    continue

                if suffix is None and (blocks[i][0] + blocks[i][2] >= len(self.firstPage)):
                    continue
                prefix = self.trimAlphaNum(prefix)
                suffix = self.trimAlphaNum(suffix)

                self.dynamicMarkings.append((prefix[-DYNAMICITY_MARK_LENGTH / 2:] if prefix else None, suffix[:DYNAMICITY_MARK_LENGTH / 2] if suffix else None))
        if len(self.dynamicMarkings) > 0:
            infoMsg = "dynamic content marked for removal (%d region%s)" % (len(self.dynamicMarkings), 's' if len(self.dynamicMarkings) > 1 else '')
            print infoMsg

     def trimAlphaNum(self, value):
        """
        Trims alpha numeric characters from start and ending of a given value

        >>> trimAlphaNum(u'AND 1>(2+3)-- foobar')
        u' 1>(2+3)-- '
        """

        while value and value[-1].isalnum():
            value = value[:-1]

        while value and value[0].isalnum():
            value = value[1:]

        return value

     def comparison(self, page):
        seqMatcher = difflib.SequenceMatcher(None)
        seqMatcher.set_seq1(self.firstPage)
        page = self.removeDynamicContent(page)
        seqMatcher.set_seq1(self.removeDynamicContent(self.firstPage))

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
            return True
        else:
            return False

     def removeDynamicContent(self, page):
        """
        Removing dynamic content from supplied page basing removal on
        precalculated dynamic markings
        """

        if page:
            for item in self.dynamicMarkings:
                prefix, suffix = item

                if prefix is None and suffix is None:
                    continue
                elif prefix is None:
                    page = re.sub(r'(?s)^.+%s' % re.escape(suffix), suffix, page)
                elif suffix is None:
                    page = re.sub(r'(?s)%s.+$' % re.escape(prefix), prefix, page)
                else:
                    #prefix = prefix.replace('\\','')
                    #suffix = suffix.replace('\\','')
                    #asdfasdf = r'(?s)%s.+%s' % (prefix, suffix)
                    #m = re.match(r'(?s)%s.+%s' % (prefix, suffix), page)
                    #if m:
                    #    print m.group(0), '\n', m.group(1)
                    page = re.sub(r'(?s)%s.+%s' % (re.escape(prefix), re.escape(suffix)), '%s%s' % (prefix, suffix), page)

        return page


def checkTimeBasedCompare(value, url):
    start = time.time()
    value = agent.adjustLateValues(value)
    value = "%s%s%s" % (PAYLOAD_DELIMITER, value, PAYLOAD_DELIMITER)
    payload = agent.extractPayload(value)
    url = "%s?%s" % (url, payload)
    response = proxyqueryPage(url)
    # code = response.getstatus()

    lastQueryDuration = calculateDeltaSeconds(start)
    deviation = stdev(kb.responseTimes)

    if deviation:
        # if len(kb.responseTimes) < MIN_TIME_RESPONSES:
        #     warnMsg = "time-based standard deviation method used on a model "
        #     warnMsg += "with less than %d response times" % MIN_TIME_RESPONSES
        #     print warnMsg

        lowerStdLimit = average(kb.responseTimes) + TIME_STDEV_COEFF * deviation
        # print lastQueryDuration,lowerStdLimit,MIN_VALID_DELAYED_RESPONSE
        retVal = (lastQueryDuration >= max(MIN_VALID_DELAYED_RESPONSE, lowerStdLimit))
        return retVal
