#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-07-05 21:46:56
# Author  : dongchuan
# Version : v1.0
# Desc     : 
import uuid
import urllib
from check404.conf.config import Config

class Common(object):
    @staticmethod
    def generateUUID():
        data = uuid.uuid1()
        return str(data).replace("-", "")

    @staticmethod
    def urlencode(value, safe="%&=-_", convall=False, limit=False, spaceplus=False):
        """
        URL encodes given value

        >>> urlencode('AND 1>(2+3)#')
        'AND%201%3E%282%2B3%29%23'
        """

        count = 0
        result = None if value is None else ""

        if value:
            if convall or safe is None:
                safe = ""

            # corner case when character % really needs to be
            # encoded (when not representing URL encoded char)
            # except in cases when tampering scripts are used
            if all(map(lambda x: '%' in x, [safe, value])):
                value = re.sub("%(?![0-9a-fA-F]{2})", "%25", value)

            while True:
                result = urllib.quote(utf8encode(value), safe)

                if limit and len(result) > Config.URLENCODE_CHAR_LIMIT:
                    if count >= len(Config.URLENCODE_FAILSAFE_CHARS):
                        break

                    while count < len(Config.URLENCODE_FAILSAFE_CHARS):
                        safe += Config.URLENCODE_FAILSAFE_CHARS[count]
                        count += 1
                        if safe[-1] in value:
                            break
                else:
                    break

            if spaceplus:
                result = result.replace(urllib.quote(' '), '+')

        return result