#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-07-05 21:46:56
# Author  : dongchuan
# Version : v1.0
# Desc     : 
# from core.utils.urlparse import urlparse
import re
import socket
import time
import urlparse3
import difflib
from difflib import SequenceMatcher
from check404.utils.requests.request import queryPage

DYNAMICITY_MARK_LENGTH = 8
UPPER_RATIO_BOUND = 0.95 
LOWER_RATIO_BOUND = 0.02
DIFF_TOLERANCE = 0.05
UPPER_RATIO_BOUND_DYN = 0.999
_UNKNOWN = 'UNKNOWN'

def checkComparison(firstPage, secondPage):
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

class HTTPCheck(object):
     def __init__(self, url):
        self.firstCode = _UNKNOWN
        self.originalPageTime = _UNKNOWN
        self.firstPage = _UNKNOWN
        self.secondPage = _UNKNOWN
        self.url = url
        self.dynamicMarkings = []
        
     def checkConnection(self):
        try:
            parsedUrl = urlparse3.parse_url(self.url)
            socket.getaddrinfo(parsedUrl.domain, None) #检测域名是否可以解析
        except Exception,e:
            print e
            return False
        try:
            self.originalPageTime = time.time()
            h_response = queryPage(self.url)
            self.firstPage = h_response.getdata()
            self.firstCode = h_response.getstatus()
            return True
        except Exception,e:
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
        delay = 0.5 - (time.time() - (self.originalPageTime or 0))
        delay = max(0, min(1, delay))
        time.sleep(delay)
        try:
            secondResponse = queryPage(self.url)
            self.secondPage = secondResponse.getdata()

            pageCodeStable = (self.firstCode == secondResponse.getstatus())
            if pageCodeStable == False:
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
