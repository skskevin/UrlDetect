safedog = '<iframe allowtransparency=" true" src="http://404.safedog.cn/'
game5 = "<div style='margin:auto;margin-top:200px;height:30px;color:white;text-align:center'><img src='/warning.gif'></div>"
weibo = '<script src="http://js.t.sinajs.cn/t4/apps/search_v6/js/base.js'
baike = '<script type="text/javascript" src="http://baike.bdimg.com/static/wiki-'
maxreturn = '<link rel="stylesheet" href="http://cdn.dragonstatic.com/parking/css/oneclick.css" type="text/css" />'

def checkwaf(page):
    if(page.find(safedog) >= 0):
        return True
    if(page.find(game5) >= 0):
        return True
    if(page.find(weibo) >= 0):
        return True
    if(page.find(baike) >= 0):
        return True
#    if(page.find(maxreturn) >= 0):
#        return True
