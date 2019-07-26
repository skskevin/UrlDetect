#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-07-24 16:16:33
# Author  : dongchuan
# Version : v1.0
# Desc     : 

import time
import pycurl
import random
import StringIO
from lib.config import kb,conf
from lib.utils.HTTPResponse import HTTPResponse
from lib.utils.common import urlencode
from lib.utils.common import calculateDeltaSeconds



default_header = conf.default_header
proxy_list = []
index = 0

CONNECTTIMEOUT = 90
TIMEOUT = 900

#FixME:有时候需要指定UA
def queryPage(url_str, noteResponseTime=True):
    try:
        start = time.time()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url_str)
        buff = StringIO.StringIO()
        curl.setopt(pycurl.CONNECTTIMEOUT, CONNECTTIMEOUT) 
        curl.setopt(pycurl.TIMEOUT, TIMEOUT) 
        curl.setopt(pycurl.WRITEFUNCTION, buff.write) 
        curl.setopt(curl.HEADER, True)
        curl.setopt(curl.HTTPHEADER, default_header)


        curl.setopt(pycurl.CONNECTTIMEOUT, 10)
        curl.setopt(pycurl.TIMEOUT, 10)
        #curl.setopt(curl.PROXY, 'http://119.188.115.23:8088')
        #curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 6.1; WOW64)
        #AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135
        #Safari/537.36")

        curl.perform()
        d_buff = buff.getvalue()
        curl.close()

        httpresponse = HTTPResponse(d_buff)
        httpresponse.begin()
        
        if noteResponseTime:
            kb.responseTimes.append(calculateDeltaSeconds(start))
        return httpresponse
    except:
        return None

def proxyqueryPage(url_str, noteResponseTime=True):
    global index
    try:

        #发送前先检测是否需要转码
        if '?' in url_str:
            line, params = url_str.split('?', 1)
            params = urlencode(params)
            url_str = "%s?%s" % (line, params)

        start = time.time()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url_str)
        buff = StringIO.StringIO()
        curl.setopt(pycurl.CONNECTTIMEOUT, CONNECTTIMEOUT) 
        curl.setopt(pycurl.TIMEOUT, TIMEOUT) 
        curl.setopt(pycurl.WRITEFUNCTION, buff.write) 
        curl.setopt(curl.HEADER, True)
        curl.setopt(curl.HTTPHEADER, default_header)

        curl.setopt(pycurl.CONNECTTIMEOUT, 10)
        curl.setopt(pycurl.TIMEOUT, 10)

        #index = random.randint(0, len(proxy_list) - 1)
        if(len(proxy_list) > 0):
            proxyvalue = proxy_list[index]
            curl.setopt(curl.PROXY,proxyvalue)
        #curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 6.1; WOW64)
        #AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135
        #Safari/537.36")

        curl.perform()
        d_buff = buff.getvalue()
        curl.close()

        httpresponse = HTTPResponse(d_buff)
        httpresponse.begin()
    
        index = index + 1
        if(index > len(proxy_list) - 1):
            index = 0

        if noteResponseTime:
            kb.responseTimes.append(calculateDeltaSeconds(start))
        return httpresponse
    except:
        return None


def checkproxyqueryPage(url_str,proxyvalue):
    try:
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url_str)
        buff = StringIO.StringIO()
        curl.setopt(pycurl.CONNECTTIMEOUT, CONNECTTIMEOUT) 
        curl.setopt(pycurl.TIMEOUT, TIMEOUT) 
        curl.setopt(pycurl.WRITEFUNCTION, buff.write) 
        curl.setopt(curl.HEADER, True)
        curl.setopt(curl.HTTPHEADER, default_header)

        curl.setopt(pycurl.CONNECTTIMEOUT, 10)
        curl.setopt(pycurl.TIMEOUT, 10)

        curl.setopt(curl.PROXY,proxyvalue)
        #curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 6.1; WOW64)
        #AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135
        #Safari/537.36")

        curl.perform()
        d_buff = buff.getvalue()
        curl.close()

        httpresponse = HTTPResponse(d_buff)
        httpresponse.begin()
    
        return httpresponse
    except:
        return None

