#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-06-03 14:04:35
# Author  : dongchuan
# Version : v1.0
# Desc     : 
import re
import os
import sys
import urllib
import chardet
import urlparse
import datetime
import simplejson
from urldetect.conf.config import Config


reload(sys)
sys.setdefaultencoding('utf8')

class Common(object):
    @staticmethod
    def filterChinese(check_str): # 过滤中文
        for ch in check_str.decode('utf-8'):
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    # 判断是否静态连接
    @staticmethod
    def filter_static(url):
        suffix = Common.get_url_ext(url)
        if suffix.lower() in Config.STATIC_SUFFIXES:
            return True
        return False

    # 获取url文件后缀
    @staticmethod
    def get_url_ext(url):
        try:
            path = urlparse.urlparse(url).path
            return os.path.splitext(path)[1]
        except:
            return False

    @staticmethod
    def url_decode(data, count=1):
        for i in xrange(count):
            data = urllib.unquote(data)
        return data

    @staticmethod
    def json_load(data):
        charset = chardet.detect(data)
        if "encoding" in charset:
            return simplejson.loads(data.decode(charset["encoding"], 'ignore'), encoding=charset["encoding"])
        return simplejson.loads(data)

