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
from lib.config import kb
from lib.utils.HTTPResponse import HTTPResponse
from lib.utils.common import urlencode
from lib.utils.common import calculateDeltaSeconds

proxy_list = []
default_header = ["Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        #"Accept-Encoding": "gzip, deflate",
        "Accept-Language: zh,zh-cn;q=0.8,en-us;q=0.5,en;q=0.3", 
        "Connection: keep-alive",
        "Cookie: PHPSESSID=0cac79e9e449cd52de688c5ef9f8d816; security=low",
        "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36"] 
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

