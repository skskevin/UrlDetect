import Strategy.sensitive_info
import Strategy.sensitive_file
import Strategy.sqlinjection
from core.request.queryPage import queryPage
from core.request.queryPage import proxyqueryPage
from core.request.queryPage import checkproxyqueryPage
from core.utils.checks import HTTPCheck
import time
import datetime
from core.utils.common import urlencode




# Strategy.sensitive_info.run('http://dne.gyyx.cn/admin.html')
# Strategy.sensitive_info.run('http://t.qq.com/cgi-bin')
# Strategy.sensitive_file.run('http://www.eos2015.com/')
# Strategy.sensitive_file.run('http://tu.duowan.com/index.php?r=view/mmcal:::')
# Strategy.sensitive_info.run('http://hd.duowan.com/log.txt')
# Strategy.sensitive_info.run('http://tu.duowan.com/log.txt')
# Strategy.sensitive_info.run('http://www.dianxin.cn/phpinfo.php')
# Strategy.sensitive_info.run('http://qxzl.7fgame.com/Web.config')
# Strategy.sensitive_info.run('http://www.175pt.com/test.aspx')
# Strategy.sensitive_info.run('http://www.eos2015.com/')
Strategy.sqlinjection.Init()
Strategy.sqlinjection.checkInjection('http://localhost/test.php?id=1')

