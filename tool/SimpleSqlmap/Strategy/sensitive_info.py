from core.request.queryPage import queryPage
from core.request.queryPage import proxyqueryPage
from core.utils.urlparse import urlparse
from core.utils.checks import HTTPCheck
from core.utils.checks import checkPageStability
from core.utils.waf import checkwaf
#from simple_http import bf_path
import socket
import uuid
import time



sensitive_dir = ["/.svn/entries","/1231fasdf123121252","/_private","/_vti_bin","/cgi-bin","/mailman","/iishelp","/iisadmin","/tsweb","/uploads","/query","/recent","/cache","/common","/shell","/readme","/main","/logfiles","/index","/default","/WebApplication1","/example","/examples","/send","/settings","/feedback","/global","/globals","/guestbook","/admin_","/admin_login","/admin_logon","/adminlogon","/client","/clients","/cmd","/INSTALL_admin","/incomming","/upload","/backend","/WebService","/aspnet","/Exchange","/WebApplication2","/signup","/scans","/webaccess","/restricted","/blog","/pics","/_logs","/_errors","/_tests","/.adm","/.admin","/secret","/owa","/db2","/mrtg","/other","/accounts","/warez","/my","/cc","/creditcards","/contact","/press","/p0rn","/pron","/new folder","/New Folder","/oldfiles","/old_files","/sysbackup","/secure","/secured","/src","/personal","/publish","/system","/work","/mail","/email","/php","/jsp","/dev","/development","/tools","/update","/updates","/util","/utils","/register","/search","/service","/services","/report","/purchase","/retail","/reseller","/app","/beta","/boot","/bug","/bugs","/buy","/auth","/authadmin","/import","/apps","/access-log","/catalog","/crypto","/cfdocs","/classes","/css","/doc","/docs","/download","/downloads","/down","/excel","/forum","/help","/etc","/prv","/source","/backup","/old","/include","/inc","/info","/dat","/data","/test","/tmp","/save","/archive","/marketing","/pass","/passwords","/files","/sales","/file","/root","/htdocs","/account","/sql","/setup","/website","/conf","/config","/install","/installer","/shop","/fpadmin","/administrator","/intranet","/inventory","/webadmin","/employees","/accounting","/tree","/pages","/access","/database","/html","/bin","/Admin_files","/credit","/public","/dbase","/priv","/customer","/customers","/asp","/java","/jdbc","/jrun","/job","/zipfiles","/pw","/public","/admin","/new","/adm","/oracle","/odbc","/mall_log_files","/WebTrend","/order","/support","/msql","/user","/demo","/demos","/demos","/bkup","/mp3","/db","/ftp","/ibill","/incoming","/member","/members","/sample","/samples","/scripts","/stats","/support","/www","/errors","/siteadmin","/backups","/testing","/internal","/~home","/~guest","/~nobody","/export","/testweb","/error_log","/network","/wp-admin","/base"]


sensitive_txt = ['/info.txt', '/pass.txt', '/password.txt', '/passwords.txt', '/users.txt', '/passwd.txt', '/dirs.txt', '/admin.txt', '/install.txt','/readme.txt', '/log.txt', '/logfile.txt', '/test.txt', '/auth_user_file.txt', '/registrations.txt', '/orders.txt']
sensitive_axd = ['/Trace.axd']
sensitive_php = ['/phpinfo.php', '/MMHTTPDB.php', '/MMHTTPDB.php', '/r57shell.php', '/r57.php', '/c99shell.php', '/c99.php', '/nstview.php', '/nst.php', '/rst.php', '/r57eng.php', '/shell.php', '/r.php', '/zehir.php', '/c-h.v2.php', '/php-backdoor.php', '/simple-backdoor.php', '/test.php']
sensitive_asp = ['/MMHTTPDB.asp', '/MMHTTPDB.asp', '/cmdasp.asp', '/admin_login.asp', '/test.asp']
sensitive_yml = ['/database.yml']
sensitive_mdb = ['/ewebeditor.mdb', '/wwForum.mdb']
sensitive_ini = ['/users.ini', '/php.ini']
sensitive_db = ['/users.db', '/admin.db']
sensitive_pw = ['/admin.pw']
sensitive_conf = ['/admin.conf']
sensitive_html = ["/struts/webconsole.html",'/admin.html', '/test.html', '/webstats.html', '/wwwstats.html', '/log.html', '/logs.html']
sensitive_cfg = ['/admin.cfg']
sensitive_htm = ['/admin.htm', '/test.htm', '/stat.htm', '/statistics.htm', '/wwwstats.htm', '/log.htm', '/logs.htm', '/orders.htm', '/registrations.htm']
sensitive_log = ['/install.log', '/errors.log', '/debug.log', '/cleanup.log', '/access.log', '/memory.log', '/server.log', '/system.log']
sensitive_inc = ['/database.inc', '/common.inc', '/db.inc', '/connect.inc', '/debug.inc', '/sql.inc']
sensitive_config = ['/Web.config']
sensitive_asax = ['/Global.asax']
sensitive_asa = ['/Global.asa']
sensitive_cs = ['/Global.asax.cs']
sensitive_bak = ['/global.bak', '/global.asa.bak', '/Global.asax.bak', '/Web.config.bak']
sensitive_rar = ['/global.rar']
sensitive_old = ['/global.old', '/global.asa.old', '/Web.config.old', '/Global.asax.old']
sensitive_orig = ['/global.orig', '/global.asa.orig', '/Global.asax.orig', '/Web.config.orig']
sensitive_bakup = ['/global.asa.bakup', '/Web.config.bakup', '/Global.asax.bakup']
sensitive_tmp = ['/global.asa.tmp', '/Web.config.tmp', '/Global.asax.tmp']
sensitive_temp = ['/Web.config.temp', '/Global.asax.temp']
sensitive_jsp = ['/test.jsp']
sensitive_aspx = ['/test.aspx']
sensitive_asmx = ['/Service.asmx']


validate_url = None
validate_data = None
out_list = []




def checkfile(element, ext_str, check_list):

    global validate_url
    global validate_data
    global out_list

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

                                        out_list.append(checkflie_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')

                                        if(validate_url != None):
                                            out_list.append(validate_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')
                                            validate_url = None

                                        #output = open('safe_dir_file.txt',
                                        #'a')
                                        #if(validate_url != None):
                                        #    output.write(validate_url + ' ' +
                                        #    str(test.firstCode) + ' ' +
                                        #    str(httpresponse.getstatus()) +
                                        #    '\n')
                                        #    validate_url = None
                                        #output.write(checkflie_url + ' ' +
                                        #str(test.firstCode) + ' ' +
                                        #str(httpresponse.getstatus()) + '\n')
                                        #output.close()
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

                                        out_list.append(checkflie_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')

                                        if(validate_url != None):
                                            out_list.append(validate_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')
                                            validate_url = None

                                        #output = open('safe_dir_file.txt',
                                        #'a')
                                        #if(validate_url != None):
                                        #    output.write(validate_url + ' ' +
                                        #    str(test.firstCode) + ' ' +
                                        #    str(httpresponse.getstatus()) +
                                        #    '\n')
                                        #    validate_url = None
                                        #output.write(checkflie_url + ' ' +
                                        #str(test.firstCode) + ' ' +
                                        #str(httpresponse.getstatus()) + '\n')
                                        #output.close()
                    else:
                        #time.sleep(1)
                        validateresponse = proxyqueryPage(checkflie_url)
                        if(validateresponse != None):
                            if(validateresponse.getstatus() == httpresponse.getstatus()):   #重新发送一次请求检测两次返回code是否一致
                                output = open('info.txt', 'a') 
                                output.write(checkflie_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')
                                output.close()
                            
def checkallfile(element):
    checkfile(element,'.txt',sensitive_txt)
    checkfile(element,'.axd',sensitive_axd)
    checkfile(element,'.php',sensitive_php)
    checkfile(element,'.asp',sensitive_asp)
    checkfile(element,'.yml',sensitive_yml)
    checkfile(element,'.mdb',sensitive_mdb)
    checkfile(element,'.ini',sensitive_ini)
    checkfile(element,'.db',sensitive_db)
    checkfile(element,'.pw',sensitive_pw)
    checkfile(element,'.conf',sensitive_conf)
    checkfile(element,'.html',sensitive_html)
    checkfile(element,'.cfg',sensitive_cfg)
    checkfile(element,'.htm',sensitive_htm)
    checkfile(element,'.log',sensitive_log)
    checkfile(element,'.inc',sensitive_inc)
    checkfile(element,'.config',sensitive_config)
    checkfile(element,'.asax',sensitive_asax)
    checkfile(element,'.asa',sensitive_asa)
    checkfile(element,'.cs',sensitive_cs)
    checkfile(element,'.bak',sensitive_bak)
    checkfile(element,'.rar',sensitive_rar)
    checkfile(element,'.old',sensitive_old)
    checkfile(element,'.orig',sensitive_orig)
    checkfile(element,'.bakup',sensitive_bakup)
    checkfile(element,'.tmp',sensitive_tmp)
    checkfile(element,'.temp',sensitive_temp)
    checkfile(element,'.jsp',sensitive_jsp)
    checkfile(element,'.aspx',sensitive_aspx)
    checkfile(element,'.asmx',sensitive_asmx)

def checkdir(element):
    global validate_url
    global validate_data
    global out_list

    guid = str(uuid.uuid1()).replace('-','')
    guid = filter(str.isalpha, guid)
    
    check404_file = "/" + guid
    check404_url = element + check404_file   
    
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
        for element_file in sensitive_dir:
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
                                        out_list.append(checkflie_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')

                                        if(validate_url != None):
                                            out_list.append(validate_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')
                                            validate_url = None

                                        #output = open('safe_dir.txt', 'a')
                                        #if(validate_url != None):
                                        #    output.write(validate_url + ' ' +
                                        #    str(test.firstCode) + ' ' +
                                        #    str(httpresponse.getstatus()) +
                                        #    '\n')
                                        #    validate_url = None
                                        #output.write(checkflie_url + ' ' +
                                        #str(test.firstCode) + ' ' +
                                        #str(httpresponse.getstatus()) + '\n')
                                        #output.close()

    else:
        for element_file in sensitive_dir:
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

            if(httpresponse.getstatus() == 301 or httpresponse.getstatus() == 302 or httpresponse.getstatus() == 401 or httpresponse.getstatus() == 200):
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

                                        out_list.append(checkflie_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')

                                        if(validate_url != None):
                                            out_list.append(validate_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')
                                            validate_url = None

                                        #output = open('safe_dir.txt', 'a')
                                        #if(validate_url != None):
                                        #    output.write(validate_url + ' ' +
                                        #    str(test.firstCode) + ' ' +
                                        #    str(httpresponse.getstatus()) +
                                        #    '\n')
                                        #    validate_url = None
                                        #output.write(checkflie_url + ' ' +
                                        #str(test.firstCode) + ' ' +
                                        #str(httpresponse.getstatus()) + '\n')
                                        #output.close()
                    else:
                        #time.sleep(1)
                        if(test.firstCode != httpresponse.getstatus()):
                            validateresponse = proxyqueryPage(checkflie_url + guid)
                            if(validateresponse != None):
                                if(validateresponse.getstatus() != httpresponse.getstatus()):   #在测试url后面加上随机生成的字符串验证是否web服务器是否处理

                                    validateresponse = proxyqueryPage(checkflie_url)
                                    if(validateresponse != None):
                                        if(validateresponse.getstatus() == httpresponse.getstatus()):   #重新发送一次请求检测两次返回code是否一致

                                            out_list.append(checkflie_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')

                                            if(validate_url != None):
                                                out_list.append(validate_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')
                                                validate_url = None

                                            #output = open('safe_dir.txt', 'a') 
                                            #output.write(checkflie_url + '      ' + str(test.firstCode) + '       ' + str(httpresponse.getstatus()) + '\n')
                                            #output.close()

def run(url_str):
    #记录解析引擎发送过来的url
    output = open('log.txt', 'a') 
    output.write(url_str + ':::\n')
    output.close()

    url = urlparse(url_str) #分割url获得分割后的路径
    #output = open('log.txt', 'a')
                               #output.write(url.url_file + '\n')
                                                          #output.write(url.url_ext
                                                                                     #+
                                                                                                                #'\n')
                                                                                                                                           #output.close()

    for element in url.path_list:   #遍历路径
            output = open('log.txt', 'a') 
            output.write(element + '\n')
            output.close()
        
            print element   #打印路径
           

            global validate_url
            global validate_data
            global out_list

            checkdir(element)

            out_writes = ''
            if(len(out_list) < 8):
                for token in out_list:
                    out_writes = out_writes + token
                if(out_writes != ''):
                    output = open('safe_dir.txt', 'a') 
                    output.write(out_writes + '  \n')
                    output.close()

            if(validate_url != None):
                output = open('safe_dir.txt', 'a') 
                output.write(validate_url + '  \n')
                output.close()

            validate_url = None
            validate_data = None
            out_list = []

            checkallfile(element)

            out_writes = ''
            if(len(out_list) < 5):
                for token in out_list:
                    out_writes = out_writes + token
                if(out_writes != ''):
                    output = open('safe_dir_file.txt', 'a') 
                    output.write(out_writes + '  \n')
                    output.close()
            
            if(validate_url != None):
                output = open('safe_dir_file.txt', 'a')
                output.write(validate_url + ' \n')
                output.close()

            validate_url = None
            validate_data = None
            out_list = []

    pass