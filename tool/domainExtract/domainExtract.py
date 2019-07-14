#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-06-17 14:04:35
# Author  : dongchuan
# Version : v1.0
# Desc     : 识别日志中的Domain和IP

TK_DOMAIN = 1
TK_IP = 2
TK_INTEGER = 3
TK_OTHER = 4

legalChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"
legalNumers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

topLevelDomain = ['biz', 'com', 'edu', 'gov', 'info', 'int', 'mil', 'name', 'net', 'org', 'pro', 'aero', 'cat', 'coop',
               'jobs', 'museum', 'travel', 'arpa', 'root', 'mobi', 'post', 'tel', 'asia', 'geo', 'kid', 'mail', 'sco',
               'web', 'xxx', 'nato', 'example', 'invalid', 'test', 'bitnet', 'csnet', 'onion', 'uucp', 'ac', 'ad', 'ae',
               'af', 'ag', 'ai', 'al', 'am', 'an', 'ao', 'aq', 'ar', 'as', 'at', 'au', 'aw', 'ax', 'az', 'ba', 'bb',
               'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'bj', 'bm', 'bn', 'bo', 'br', 'bs', 'bt', 'bv', 'bw', 'by', 'bz',
               'ca', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci', 'ck', 'cl', 'cm', 'cn', 'co', 'cr', 'cu', 'cv', 'cx', 'cy',
               'cz', 'de', 'dj', 'dk', 'dm', 'do', 'dz', 'ec', 'ee', 'eg', 'eh', 'er', 'es', 'et', 'eu', 'fi', 'fj',
               'fk', 'fm', 'fo', 'fr', 'ga', 'gb', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gl', 'gm', 'gn', 'gp', 'gq',
               'gr', 'gs', 'gt', 'gu', 'gw', 'gy', 'hk', 'hm', 'hn', 'hr', 'ht', 'hu', 'id', 'ie', 'il', 'im', 'in',
               'io', 'iq', 'ir', 'is', 'it', 'je', 'jm', 'jo', 'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn', 'kp', 'kr',
               'kw', 'ky', 'kz', 'la', 'lb', 'lc', 'li', 'lk', 'lr', 'ls', 'lt', 'lu', 'lv', 'ly', 'ma', 'mc', 'md',
               'me', 'mg', 'mh', 'mk', 'ml', 'mm', 'mn', 'mo', 'mp', 'mq', 'mr', 'ms', 'mt', 'mu', 'mv', 'mw', 'mx',
               'my', 'mz', 'na', 'nc', 'ne', 'nf', 'ng', 'ni', 'nl', 'no', 'np', 'nr', 'nu', 'nz', 'om', 'pa', 'pe',
               'pf', 'pg', 'ph', 'pk', 'pl', 'pm', 'pn', 'pr', 'ps', 'pt', 'pw', 'py', 'qa', 're', 'ro', 'rs', 'ru',
               'rw', 'sa', 'sb', 'sc', 'sd', 'se', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sr', 'st',
               'su', 'sv', 'sy', 'sz', 'tc', 'td', 'tf', 'tg', 'th', 'tj', 'tk', 'tl', 'tm', 'tn', 'to', 'tp', 'tr',
               'tt', 'tv', 'tw', 'tz', 'ua', 'ug', 'uk', 'um', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 'vi', 'vn',
               'vu', 'wf', 'ws', 'ye', 'yt', 'yu', 'za', 'zm', 'zw']

datas = []
ids = []
extension_list = []


class DomainTokenizer():
    def __init__(self):
        self.urls = []

    def RunParser(self, zInfo):
        i = 0
        while (i < len(zInfo)):
            sLastTokenz = zInfo[i:len(zInfo)]
            sLastTokenn = 0
            sLastTokenn, tokenType = self.GetToken(sLastTokenz, zInfo, i)
            i = i + sLastTokenn

    def isLegalChar(self, zv):
        if zv in legalNumers or zv in legalChars:
            return True
        else:
            return False

    def GetToken(self, z, zInfo, sLastTokenn):
        i = 0
        zv = z[0]
        if zv in legalNumers:
            i = 0
            reti = 0
            tokenType = TK_IP

            ip_v1 = False
            ip_v2 = False
            ip_v3 = False
            ip_v4 = False

            while (i < len(z) and z[i].isdigit()):
                i = i + 1
                ip_v1 = True
                reti = i
            if i < len(z) and z[i] == '.':
                i = i + 1
                reti = i
            else:
                tokenType = TK_OTHER
                reti = 1

            urltoken_str = z[i:len(z)]
            urltoken_str = urltoken_str.lower()
            for item in topLevelDomain:
                if urltoken_str.find(item)==0:
                    i = i + len(item)
                    reti=i
                    tokenType = TK_DOMAIN
                    break

            while (i < len(z) and z[i].isdigit()):
                i = i + 1
                ip_v2 = True
            if i < len(z) and z[i] == '.':
                i = i + 1
            else:
                if tokenType != TK_DOMAIN:
                    tokenType = TK_OTHER
                    reti = 1

            urltoken_str = z[i:len(z)]
            urltoken_str = urltoken_str.lower()
            for item in topLevelDomain:
                if urltoken_str.find(item)==0:
                    i = i + len(item)
                    reti=i
                    tokenType = TK_DOMAIN
                    break

            while (i < len(z) and z[i].isdigit()):
                i = i + 1
                ip_v3 = True
            if i < len(z) and z[i] == '.':
                i = i + 1
            else:
                if tokenType != TK_DOMAIN:
                    tokenType = TK_OTHER
                    reti = 1

            urltoken_str = z[i:len(z)]
            urltoken_str = urltoken_str.lower()
            for item in topLevelDomain:
                if urltoken_str.find(item)==0:
                    i = i + len(item)
                    reti=i
                    tokenType = TK_DOMAIN
                    break

            while (i < len(z) and z[i].isdigit()):
                i = i + 1
                ip_v4 = True

            if i < len(z) and z[i] == ':':
                i = i + 1
            while (i < len(z) and z[i].isdigit()):
                i = i + 1

            if ip_v1 and ip_v2 and ip_v3 and ip_v4:
                self.urls.append(z[0:i])
                return reti, tokenType
            else:
                if tokenType != TK_DOMAIN:
                    tokenType = TK_OTHER
                    reti = 1

            while (i < len(z) and self.isLegalChar(z[i])):
                i = i + 1
                reti = i

            while i < len(z) and z[i] == '.':
                i = i + 1
                urltoken_str = z[i:len(z)]
                urltoken_str = urltoken_str.lower()
                for item in topLevelDomain:
                    if urltoken_str.find(item)==0:
                        i = i + len(item)
                        reti=i
                        tokenType = TK_DOMAIN
                        break
                while (i < len(z) and self.isLegalChar(z[i])):
                    i = i + 1
                    reti = i
                if i < len(z) and z[i] == ':':
                    i = i + 1
                while (i < len(z) and z[i].isdigit()):
                    i = i + 1
                    reti = i
            if tokenType == TK_DOMAIN:
                check_url = z[0:i]
                if check_url.find(':') >= 0:
                    check_url = check_url[0:check_url.find(':')]
                for item in topLevelDomain:
                    pos = check_url.find('.' + item)
                    if pos > -1 and (pos + len(item) + 1 == len(check_url)):
                        self.urls.append(z[0:i])
            else:
                reti = 1

            return reti, tokenType

        elif self.isLegalChar(zv):
            i = 0
            reti = 0
            tokenType = TK_OTHER
            while (i < len(z) and self.isLegalChar(z[i])):
                i = i + 1
                reti = i

            while i < len(z) and z[i] == '.':
                i = i + 1
                urltoken_str = z[i:len(z)]
                urltoken_str = urltoken_str.lower()
                for item in topLevelDomain:
                    if urltoken_str.find(item)==0:
                        i = i + len(item)
                        reti=i
                        tokenType = TK_DOMAIN
                        break
                while (i < len(z) and self.isLegalChar(z[i])):
                    i = i + 1
                    reti = i
                if i < len(z) and z[i] == ':':
                    i = i + 1
                while (i < len(z) and z[i].isdigit()):
                    i = i + 1
                    reti = i
            if tokenType == TK_DOMAIN:
                check_url = z[0:i]
                if check_url.find(':') >= 0:
                    check_url = check_url[0:check_url.find(':')]
                for item in topLevelDomain:
                    pos = check_url.find('.' + item)
                    if pos > -1 and (pos + len(item) + 1 == len(check_url)):
                        self.urls.append(z[0:i])

            else:
                reti = 1

            return reti, tokenType
        else:
            return 1, TK_OTHER



#demo = ["192.168.1.1", "mp3.com","http:www.g.cn","http:\www.g.cn","http:\\/\www.g.cn", "admin:@www.g.cn","http://10.10.10.10:8080/?a=1","file://test11.com:8090/file","mailto:majy@corp.com","username:password@g.cn"]
demo = ["http:\\/\www.baidu.com www.sina.com.cn username:password@www.g.cn file://10.1.1.1/aa ftp://test:test@192.168.0.1:21/profile"]
for d in demo:
    parser = DomainTokenizer()
    parser.RunParser(d)
    print parser.urls
