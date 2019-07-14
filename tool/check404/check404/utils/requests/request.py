#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-07-06 17:50:53
# Author  : dongchuan
# Version : v1.0
# Desc     : 
import pycurl
import StringIO
import random
from check404.utils.common import Common
from response import HTTPResponse

proxy_list = []
default_header = ["Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        #"Accept-Encoding": "gzip, deflate",
        "Accept-Language: zh,zh-cn;q=0.8,en-us;q=0.5,en;q=0.3", 
        "Connection: keep-alive",
        "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36"] 
index = 0

CONNECTTIMEOUT = 90
TIMEOUT = 900

#FixME:有时候需要指定UA
def queryPage(url):
    try:
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
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
    
        return httpresponse
    except:
        return None

def proxyqueryPage(url):
    global index
    try:

        #发送前先检测是否需要转码
        if '?' in url:
            line, params = url.split('?', 1)
            params = Common.urlencode(params)
            url = "%s?%s" % (line, params)


        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
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
        return httpresponse
    except:
        return None


def checkproxyqueryPage(url,proxyvalue):
    try:
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
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

