#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-06-04 11:03:26
# Author  : dongchuan
# Version : v1.0
# Desc     :  词法分析器
# url请求参数中,只包含:字母 数字 _ -,则认为此参数安全,标白

TK_STRING = 1
TK_INTEGER = 2
TK_UNDER = 3  # _
TK_STRAIGHT = 4  # -
TK_FLOAT = 5
TK_OTHER = 999

legalChars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
legalNumers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
legalTypes = [TK_STRING, TK_INTEGER, TK_UNDER, TK_STRAIGHT, TK_FLOAT, TK_OTHER]

class URLTokenizer():
    # def __init__(self):
    #     self.url_safe = False

    def URLRunParser(self, zUrl):
        i = 0
        url_safe = False
        sLastTokenType = 0
        while (i < len(zUrl)):
            sLastTokenz = zUrl[i:len(zUrl)]
            sLastTokenn = 0
            sLastTokenn, tokenType = self.urlGetToken(sLastTokenz, zUrl, i)
            if sLastTokenn >= 1:
                words = zUrl[i:i + sLastTokenn]

                if (tokenType in legalTypes) and sLastTokenType == 0:
                    url_safe = True
                elif sLastTokenType == 1 and tokenType == 2:
                    url_safe = True
                elif sLastTokenType == 2 and tokenType == 1:
                    url_safe = True

                elif sLastTokenType == 1 and tokenType == 3:
                    url_safe = True
                elif sLastTokenType == 3 and tokenType == 1:
                    url_safe = True

                elif sLastTokenType == 2 and tokenType == 3:
                    url_safe = True
                elif sLastTokenType == 3 and tokenType == 2:
                    url_safe = True

                elif sLastTokenType == 1 and tokenType == 4:
                    url_safe = True
                elif sLastTokenType == 4 and tokenType == 1:
                    url_safe = True

                elif sLastTokenType == 2 and tokenType == 4:
                    url_safe = True
                elif sLastTokenType == 4 and tokenType == 2:
                    url_safe = True

                elif sLastTokenType == 1 and tokenType == 5:
                    url_safe = True
                elif sLastTokenType == 5 and tokenType == 1:
                    url_safe = True

                elif sLastTokenType == 5 and tokenType == 4:
                    url_safe = True
                elif sLastTokenType == 4 and tokenType == 5:
                    url_safe = True
                else:
                    url_safe = False
                    break

            sLastTokenType = tokenType
            i = i + sLastTokenn

        return url_safe

    def urlGetToken(self, z, zUrl, sLastTokenn):
        i = 0
        zv = z[0]
        if zv in legalNumers:
            i = 0
            tokenType = TK_INTEGER
            while (i < len(z) and z[i].isdigit()):
                i = i + 1
            if i < len(z) and z[i] == '.':
                i = i + 1
                while (i < len(z) and (z[i].isdigit())):
                    i = i + 1
                tokenType = TK_FLOAT
            # if i < len(z):
            #     ta = 0
            #     tb = 0
            #     tc = 0
            #     if (i < len(z)):
            #         ta = z[i]
            #     if (i + 1 < len(z)):
            #         tb = z[i]
            #     if (i + 2 < len(z)):
            #         tc = z[i]

            #     if ta == 'e' or ta == 'E' and tb.isdigit() or ((tb == '+' or tb == '-') and tc.isdigit()):
            #         i += 2
            #         while (i < len(z) and z[i].isdigit()):
            #             i = i + 1
            #         tokenType = TK_FLOAT
            return i, tokenType
        elif zv == '_':
            return 1, TK_UNDER
        elif zv == '-':
            return 1, TK_STRAIGHT
        elif zv in legalChars:
            i = 0
            tokenType = TK_STRING
            while (i < len(z) and (z[i] in legalChars)):
                i = i + 1
            return i, tokenType

        return 1, TK_OTHER


# parser = URLTokenizer()
# print parser.URLRunParser("9DC608A19146D3E147BC8040855A3D1E")
# print parser.url_safe