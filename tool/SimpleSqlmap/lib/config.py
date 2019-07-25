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

kb = AttribDict()
kb.responseTimes = []
kb.dbms = None
