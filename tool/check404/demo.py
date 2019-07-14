#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-07-06 18:02:05
# Author  : dongchuan
# Version : v1.0
# Desc     : 
import time
import random
import requests
import urlparse
from check404.utils.requests.request import queryPage
from check404.utils.httpcheck import HTTPCheck, checkComparison
from check404.utils.common import Common
from check404.utils.waf import checkwaf

sensitive_path = ["/.svn/entries","/www/46/2019-04/75873.html","/products/1901129838.html", "/articles/web/206244.html","/News/2017/08/232596.shtml"]

	

def run(url):
    uuidStr = Common.generateUUID()
    nonExistentUrl = "%s/%s" % (url,uuidStr)
    httptest = HTTPCheck(nonExistentUrl)
    if not httptest.checkConnection():
        print "%s:连接失败" % url


    for count in xrange(5):
        # time.sleep(random.random())
        if(httptest.checkStability()):  #检测稳定性，并且找出动态内容
            if len(httptest.dynamicMarkings) > 0:
                break
        else:
            print "%s:连接不稳定" % nonExistentUrl

    #begin to scan
    if httptest.firstCode == 200:
        for d in sensitive_path:
            checkUrl = "%s%s" % (url, d)
            response1 = queryPage(checkUrl)
            if not response1:
                print "%s:get nothing" % checkUrl
                continue
            if checkwaf(response1.getdata()):
                print "有狗....算了...."
                continue    #检测到是waf则跳过

            if(httptest.firstCode != response1.getstatus()): #判断返回码是不是200
                continue
            httptest.firstPage = httptest.firstPage.lower()
            response1.data = response1.data.lower()

            if(httptest.firstPage.find(uuidStr.lower()) >= 0):    #判断用uuid产生的url值是否存在html中 或 已经检测过？
                httptest.firstPage = httptest.firstPage.replace(uuidStr.lower(),'')
            if(response1.data.find(d.lower().strip('/')) >= 0):    #判断用uuid产生的url值是否存在html中 或 已经检测过？
                response1.data = response1.data.replace(d.lower().strip('/'),'')

            if httptest.comparison(response1.getdata()): #请求结果和404页面对比
                print "%s:  404" % checkUrl
            else:
                response2 = queryPage(checkUrl)
                if response2 != None:
                        response2.data = response2.data.lower()
                        if(response2.data.find(d.lower().strip('/')) >= 0):    #判断用guid产生的url值是否存在html中 或 已经检测过？
                            response2.data = response2.data.replace(d.lower().strip('/'),'')

                        if checkComparison(response2,response1):
                            #如果返回没有内容则跳过
                            if(response2.getdata() == ''):
                                continue
                            validate_data = None
                            validate_data = HTTPCheck(checkUrl)
                            validate_data.firstCode = response1.getstatus()
                            validate_data.firstPage = response1.getdata()
                            if checkwaf(validate_data.firstPage):
                                continue    #检测到是waf则跳过

                            print "%s:  active" % checkUrl
    else:
        for d in sensitive_path:
            checkUrl = "%s%s" % (url, d)
            response1 = queryPage(checkUrl)
            if not response1:
                print "%s:get nothing" % checkUrl
                continue
            if checkwaf(response1.getdata()):
                print "有狗....算了...."
                continue    #检测到是waf则跳过

            if response1.getstatus() == 200:
                httptest.firstPage = httptest.firstPage.lower()
                response1.data = response1.data.lower()

                if(httptest.firstPage.find(uuidStr.lower()) >= 0):    #判断用uuid产生的url值是否存在html中 或 已经检测过？
                    httptest.firstPage = httptest.firstPage.replace(uuidStr.lower(),'')
                if(response1.data.find(d.lower().strip('/')) >= 0):    #判断用uuid产生的url值是否存在html中 或 已经检测过？
                    response1.data = response1.data.replace(d.lower().strip('/'),'')

                response2 = queryPage(checkUrl)
                if response2 != None:
                        response2.data = response2.data.lower()
                        if(response2.data.find(d.lower().strip('/')) >= 0):    #判断用guid产生的url值是否存在html中 或 已经检测过？
                            response2.data = response2.data.replace(d.lower().strip('/'),'')

                        if checkComparison(response2,response1):
                            #如果返回没有内容则跳过
                            if(response2.getdata() == ''):
                                continue

                            print "%s:  active" % checkUrl
            
            else:
                # if httptest.firstCode == response1.getstatus():
                print "%s:  404" % checkUrl

    

if __name__ == '__main__':
    urllist = [
        # "http://b.liebao.cn",
        # "http://e.dangdang.com",
        # "https://www.baidu.com",
        "http://xxd.gyyx.cn"
    ]
    for url in urllist:
        run(url)
    
