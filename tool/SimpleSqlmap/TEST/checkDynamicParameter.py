from core.utils.checks import checkDynParam
from core.utils.common import paramToDict

from urlparse import urlparse

def run(url):
    uri = ""
    place = {}

    if url.startswith("http://") or url.startswith("https://"):
        place['uri'] = url

        paramters = urlparse(url).query

        if not paramters:
            return
        else:
            output = open('checkDynParam.txt', 'a') 
            output.write('\n\n' + url + ':::\n')
            output.close()
            print url
            place['paramstring'] = paramters
            paramDict = dict()

            paramDict = paramToDict(place['paramstring'])

            place['paramdict'] = paramDict

            for (key, value) in paramDict.items():
                if not value:
                    print 'Empty Parameter Value, key={0} value= '.format(key)
                    output = open('checkDynParam.txt', 'a') 
                    output.write(key + ' Empty \n')
                    output.close()

                elif checkDynParam(place, key, value):
                    print 'Static Parameter key={0}, value={1}'.format(key, value)
                    output = open('checkDynParam.txt', 'a') 
                    output.write(key + '=' + value + ' Static \n')
                    output.close()
                else:
                    print 'Dynamic Parameter key={0}, value={1}'.format(key, value)
                    output = open('checkDynParam.txt', 'a') 
                    output.write(key + '=' + value + ' Dynamic \n')
                    output.close()

