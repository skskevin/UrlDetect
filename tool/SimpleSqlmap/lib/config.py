#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-07-17 21:51:57
# Author  : dongchuan
# Version : v1.0
# Desc     : 
import os
from data import AttribDict


conf = AttribDict()

projectDir = os.path.dirname(os.path.dirname(__file__))
errorsXML = os.path.join(projectDir, "xml/errors.xml")
boundariesXML = os.path.join(projectDir, "xml/boundaries.xml")
payloadPath = os.path.join(projectDir, "xml/payloads")

conf.errorsXML = errorsXML
conf.boundariesXML = boundariesXML
conf.payloadPath = payloadPath
conf.originUrl = None
conf.ErrorPage = None
conf.url = None
conf.cache = None
conf.boundaries = []
conf.parameters = {}
conf.tests = []
conf.timeSec = 5

conf.default_header = ["Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        #"Accept-Encoding": "gzip, deflate",
        "Accept-Language: zh,zh-cn;q=0.8,en-us;q=0.5,en;q=0.3", 
        "Connection: keep-alive",
        "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36"] 


kb = AttribDict()
kb.responseTimes = []
kb.dbms = None
