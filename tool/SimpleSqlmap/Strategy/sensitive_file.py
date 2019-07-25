from core.request.queryPage import queryPage
from core.request.queryPage import proxyqueryPage
from core.utils.urlparse import urlparse
from core.utils.checks import HTTPCheck
from core.utils.checks import checkPageStability
from core.utils.waf import checkwaf
#from simple_http import bf_file
import socket
import uuid
import time


ext_list = [".jsp",".asp",".php",".do",".php",".aspx"]


sensitive_ext = [".old",".OLD",".bak",".BAK",".zip",".ZIP",".gz",".tar.gz",".temp",".save",".backup",".orig",".000","~1",".cs",".pas",".vb",".java",".class",".sav",".saved",".rar",".src",".tmp",".inc",".copy"]

validate_url = None
validate_data = None


def checkfile(element, ext_str, check_list):

    global validate_url
    global validate_data

    guid = str(uuid.uuid1()).replace('-','')
    guid = filter(str.isalpha, guid)
    
    check404_file = "/" + guid + ext_str
    check404_url = element + check404_file  #根据路径生成绝对不存在的文件，探测服务器是否是自定义404

    #time.sleep(1)
    test = HTTPCheck(check404_url)
    if(test.checkConnection()): #检测构造的探测自定义404地址是否能访问
        #print element + ' Coon ok'
        pass
    else:
        output = open('Error.txt', 'a') 
        output.write(check404_url + '  not conn\n')
        output.close()
        return    #检测到如果连接出现问题则跳过
                  #time.sleep(1)
    count = 0
    while count < 5:
        count = count + 1
        if(test.checkStability()):  #检测url稳定性，并且找出动态内容
            if(len(test.dynamicMarkings) > 0):
                break
        else:
            output = open('Error.txt', 'a') 
            output.write(check404_url + '  not Stability\n')
            output.close()
            return
           
    if(test.firstCode == 200):  #判断该url的路径是否为自定义404
        for element_file in check_list:
            #print element_flie
            checkflie_url = element + element_file

            #time.sleep(1)
            httpresponse = proxyqueryPage(checkflie_url)

            if(httpresponse == None):
                output = open('Error.txt', 'a') 
                output.write(checkflie_url + 'not get\n')
                output.close()
                continue

            if checkwaf(httpresponse.getdata()):
                continue    #检测到是waf则跳过

            if(test.firstCode != httpresponse.getstatus()): #判断返回码是不是200
                continue

            test.firstPage = test.firstPage.lower()
            httpresponse.data = httpresponse.data.lower()

            if(test.firstPage.find(check404_file.lower().strip('/')) >= 0):    #判断用guid产生的url值是否存在html中 或 已经检测过？
                test.firstPage = test.firstPage.replace(check404_file.lower().strip('/'),'')
            if(httpresponse.data.find(element_file.lower().strip('/')) >= 0):    #判断用guid产生的url值是否存在html中 或 已经检测过？
                httpresponse.data = httpresponse.data.replace(element_file.lower().strip('/'),'')

            #要加入url插入html过滤的问题
            if(test.comparison(httpresponse.getdata())):
                #print checkflie_url + ' is safe'
                pass
            else:
                #print checkflie_url + ' not safe'
                #if(httpresponse.getdata().find('<span
                #class="r-tip01"><script>document.write(error_403);</script></span>')
                #< 0 and httpresponse.getdata().find('{"msg":"uri not
                #allow!"}') < 0 and httpresponse.getdata().find('<script
                #type="text/javascript" charset="utf-8"
                #src="http://errors.waf.aliyun.com/ecswaf_errorstat.js"></script>')
                #< 0): #判断是否是waf判定为危险请求
                    #time.sleep(1)
                    validateresponse = proxyqueryPage(checkflie_url)
                    if(validateresponse != None):
                        #if(validateresponse.getstatus() ==
                        #httpresponse.getstatus()): #重新发送一次请求检测两次返回code是否一致

                        validateresponse.data = validateresponse.data.lower()
                        if(validateresponse.data.find(element_file.lower().strip('/')) >= 0):    #判断用guid产生的url值是否存在html中 或 已经检测过？
                            validateresponse.data = validateresponse.data.replace(element_file.lower().strip('/'),'')

                        if checkPageStability(validateresponse,httpresponse):
                            #如果返回没有内容则跳过
                            if(validateresponse.getdata() == ''):
                                continue
                            if(validate_data == None):    #判断验证缓存是否存在
                                    #添加验证缓存 检测是否是误报
                                    validate_data = HTTPCheck(checkflie_url)
                                    validate_url = checkflie_url

                                    validate_data.firstCode = httpresponse.getstatus()
                                    validate_data.firstPage = httpresponse.getdata()

                                    if checkwaf(validate_data.firstPage):
                                        validate_url = None
                                        validate_data = None
                                        continue    #检测到是waf则跳过

                                    #检测等级动态内容
                                    validate_data.checkPageStability(validateresponse.getdata(),validateresponse.getstatus())
                                    
                            else:
                                    pass
                                    # 检测验证结果是否和缓存验证是否一致 如果一致则证明误报
                                    if validate_data.comparison(httpresponse.getdata()):
                                        validate_url = None
                                        pass
                                    else:
                                        #if checkwaf(httpresponse.getdata()):
                                        #    continue

                                        output = open('safe_file.txt', 'a') 
                                        if(validate_url != None):
                                            output.write(validate_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')
                                            validate_url = None
                                        output.write(checkflie_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')
                                        output.close()
                #pass
    else:
        for element_file in check_list:
            #print element_flie
            checkflie_url = element + element_file

            #time.sleep(1)
            httpresponse = proxyqueryPage(checkflie_url)

            if(httpresponse == None):
                output = open('Error.txt', 'a') 
                output.write(checkflie_url + '  not get\n')
                output.close()
                continue

            if checkwaf(httpresponse.getdata()):
                continue    #检测到是waf则跳过

            if(httpresponse.getstatus() != test.firstCode):
                #if(httpresponse.getdata().find('<span
                #class="r-tip01"><script>document.write(error_403);</script></span>')
                #< 0 and httpresponse.getdata().find('{"msg":"uri not
                #allow!"}') < 0 and httpresponse.getdata().find('<script
                #type="text/javascript" charset="utf-8"
                #src="http://errors.waf.aliyun.com/ecswaf_errorstat.js"></script>')
                #< 0): #判断是否是waf判定为危险请求
                    #print checkflie_url + ' not safe'
                    if(httpresponse.getstatus() == 200):    #判断检测地址是否能正常访问

                        test.firstPage = test.firstPage.lower()
                        httpresponse.data = httpresponse.data.lower()

                        if(test.firstPage.find(check404_file.lower().strip('/')) >= 0):    #判断用guid产生的url值是否存在html中 或 已经检测过？
                            test.firstPage = test.firstPage.replace(check404_file.lower().strip('/'),'')
                        if(httpresponse.data.find(element_file.lower().strip('/')) >= 0):    #判断用guid产生的url值是否存在html中 或 已经检测过？
                            httpresponse.data = httpresponse.data.replace(element_file.lower().strip('/'),'')


                        #time.sleep(1)
                        validateresponse = proxyqueryPage(checkflie_url)
                        if(validateresponse != None):
                            #if(validateresponse.getstatus() ==
                            #httpresponse.getstatus()): #重新发送一次请求检测两次返回code是否一致

                            validateresponse.data = validateresponse.data.lower()
                            if(validateresponse.data.find(element_file.lower().strip('/')) >= 0):    #判断用guid产生的url值是否存在html中 或 已经检测过？
                                validateresponse.data = validateresponse.data.replace(element_file.lower().strip('/'),'')

                            if checkPageStability(validateresponse,httpresponse):
                                #如果返回没有内容则跳过
                                if(validateresponse.getdata() == ''):
                                    continue
                                if(validate_data == None):    #判断验证缓存是否存在

                                    #添加验证缓存 检测是否是误报
                                    validate_data = HTTPCheck(checkflie_url)
                                    validate_url = checkflie_url

                                    validate_data.firstCode = httpresponse.getstatus()
                                    validate_data.firstPage = httpresponse.getdata()

                                    if checkwaf(validate_data.firstPage):
                                        validate_url = None
                                        validate_data = None
                                        continue    #检测到是waf则跳过

                                    #检测等级动态内容
                                    validate_data.checkPageStability(validateresponse.getdata(),validateresponse.getstatus())

                                   
                                else:
                                    pass
                                    # 检测验证结果是否和缓存验证是否一致 如果一致则证明误报
                                    if validate_data.comparison(httpresponse.getdata()):
                                        validate_url = None
                                        pass
                                    else:
                                        #if checkwaf(httpresponse.getdata()):
                                        #    continue

                                        output = open('safe_file.txt', 'a') 
                                        if(validate_url != None):
                                            output.write(validate_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')
                                            validate_url = None
                                        output.write(checkflie_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')
                                        output.close()
                    else:
                        #time.sleep(1)
                        validateresponse = proxyqueryPage(checkflie_url)
                        if(validateresponse != None):
                            if(validateresponse.getstatus() == httpresponse.getstatus()):   #重新发送一次请求检测两次返回code是否一致
                                output = open('info.txt', 'a') 
                                output.write(checkflie_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')
                                output.close()






def run(url_str):
    output = open('log.txt', 'a') 
    output.write(url_str + ':::\n')
    output.close()

    url = urlparse(url_str) #分割url获得分割后的路径

    if url.url_ext in ext_list:  #后缀名是否需要检测
        url_test = url.url_file + url.url_ext
        if url_test not in bf_file:  #判断该文件是否检测过漏洞
            bf_file.add(url_test)
            print url.url_file + url.url_ext
            checkfile(url.url_file,url.url_ext,sensitive_ext)
            checkfile(url.url_file + url.url_ext,url.url_ext,sensitive_ext)

            global validate_url
            global validate_data

            if(validate_url != None):
                output = open('safe_file.txt', 'a') 
                output.write(validate_url + '  \n')
                output.close()

            validate_url = None
            validate_data = None