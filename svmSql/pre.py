#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-06-14 11:22:08
# Author  : dongchuan
# Version : v1.0
# Desc     : 
import re
import urlparse
import urllib


if __name__ == '__main__':
    with open("badqueries.txt") as f:
        for line in f:
            line = re.sub(r'\r|\n','', line)
            if "?" in line:
                 # inf = line.split("?")[1]
                 result = urlparse.urlparse(line)
                 query = result.query
                 params = urlparse.parse_qsl(query, True)
                 for k, v in params:
                     if re.search(r'union',v,re.IGNORECASE):
                         print urllib.unquote(v)
            else:
                # if re.search(r'union',line,re.IGNORECASE):
                #     print urllib.unquote(line)
                # else:
                print line
