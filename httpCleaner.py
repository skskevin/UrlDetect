#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-06-03 14:04:35
# Author  : dongchuan
# Version : v1.0
# Desc     : Http过滤器：过滤掉正常的URL，减少后续机器学习的数据压力
import re
import sys
import urlparse
import simplejson
from urldetect.conf.config import Config
from urldetect.utils.common import Common
from urldetect.utils.URLTokenizer import URLTokenizer



def httpFilter(request):
    if "method"  not in request:
        return True
    if "response.code" not in request:
        return True
    if str(request["response.code"]) != "200":
        return True
    if request["method"] not in ["GET", "POST"]:
        return True

    if "request.url" not in request:
        return True

    if Common.filter_static(request["realUrl"]):
        return True

    return False


def paramValFilter(paramVal):
    if not paramVal:
        return True
    if sys.getsizeof(paramVal) >= 32000: #参数大于32Kb 忽略
        return True
    #str.isdigit(): True 只包含数字
    if paramVal.isdigit():
        return True
    #str.isalpha()：True 只包含字母
    if paramVal.isalpha():
        return True
    #str.isalnum()：True 只包含字母或者数字
    if paramVal.isalnum():
        return True
    if Common.filterChinese(paramVal):
        return True


    return False

def getDeepJsonVal(data, result=[]):
    if isinstance(data, dict):
        for key, value in data.items():
            getDeepJsonVal(value, key, result)
    elif isinstance(data, list):
        for value in data:
            getDeepJsonVal(value)
    else:
        if isinstance(data, unicode) and  ('{' in data or '[' in data):
            try:
                getDeepJsonVal(simplejson.loads(data))
            except:
                if not paramValFilter(data):
                    result.append(data)
        else:
            if not paramValFilter(data):
                result.append(data)
    return result

def parseJson(request):
    try:
        reqbody = request["request.body"]
        return getDeepJsonVal(simplejson.loads(reqbody))
    except:
        try:
            result = []
            m = re.findall(r'"\w+":".*?"',reqbody)
            if m:
                for p in m:
                    result.append(p.split(':', 1)[1])
            else:
                m = re.findall(r'"\w+":\d+',reqbody)
                if m:
                    for p in m:
                        result.append(p.split(':', 1)[1])
            return result
        except Exception, e:
            # print "parseJson:", e, request
            return []

def getQueryString(request):
    data = []
    try:
        url = request["request.url"]
        result = urlparse.urlparse(url)
        query = result.query
        # urlparse.parse_qsl解析url请求切割参数时，遇到';'会截断，导致获取的参数值缺失';'后面的内容
        if ";" in query:
            query = re.sub(r';', '@@@@', query)

        params = urlparse.parse_qsl(query, True)
        for k, v in params:
            if not v:
                continue
            # 恢复分号
            if '@@@@' in v:
                v = re.sub(r'@@@@', ';', v)
            if paramValFilter(v):
                continue
            data.append(v)
    except Exception, e:
        print "parse query error:", e, request

    return data




if __name__ == '__main__':
    parser = URLTokenizer()

    with open("data/log.txt") as f:
        for line in f:
            try:
                request = Common.json_load(line)  

                if httpFilter(request):
                    continue    

                if request["method"].upper() == "GET":
                    if "request.params" not in request or not request["request.params"]:
                        continue
                    paramValList = getQueryString(request)
                if request["method"].upper() == "POST":
                    if "request.body" not in request or not request["request.body"]:
                        continue
                    paramValList = getDeepJsonVal(parseJson(request))
                
                flag = "normal"
                for p in paramValList:
                    try:
                        print p, parser.URLRunParser(str(p))
                        if not parser.URLRunParser(str(p)): # 所有参数符合词法-标白，否则流入下一步处理
                            flag = "abnormal"
                            break
                    except Exception,e: 
                        print "URLTokenizer:",e
                
                if flag == "normal":
                    print "normal", request["request.url"]
                else:
                    print "abnormal",request["request.url"]
                
            except Exception, e:
                print "main:", e, request     
