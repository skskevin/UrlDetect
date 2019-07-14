#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime    : 2019-06-17 14:04:35
# Author  : dongchuan
import re
from domainExtract import DomainTokenizer
from timeit import timeit


ss='''/log?c=5d47e4aa-8d11-4ac9-b9f8-b05eff6ff4c1,
{"kubernetes":{"name":"www.test.cn","mail":"username:password@www.g.cn","ftp":"ftp://test:test@192.168.0.1:21/profile","host":"192.168.1.1","master_url":"http:\\/\www.baidu.com"}}'''

def tokenize():
    parser = DomainTokenizer()
    parser.RunParser(ss)
    # print parser.urls


#((((ftp:|https:|http:)([\Q/\\E])*)|())(((%[0-9a-fA-F][0-9a-fA-F])|([a-zA-Z0-9])|([\Q$-_.+!*'(),;?&=\E]))+(:((%[0-9a-fA-F][0-9a-fA-F])|([a-zA-Z0-9])|([\Q$-_.+!*'(),;?&=\E]))*)?@)?(((((([a-zA-Z0-9]){1}([a-zA-Z0-9\-])*([a-zA-Z0-9]{1}))|([a-zA-Z0-9]))\.)+(biz|com|edu|gov|info|int|mil|name|net|org|pro|aero|cat|coop|jobs|museum|travel|arpa|root|mobi|post|tel|asia|geo|kid|mail|sco|web|xxx|nato|example|invalid|test|bitnet|csnet|onion|uucp|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cu|cv|cx|cy|cz|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|st|su|sv|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|um|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw))|([0-9]{1,3}(\.[0-9]{1,3}){3}))(\:([0-9]+))?(([\Q/\\E])+((((%[0-9a-fA-F][0-9a-fA-F])|([a-zA-Z0-9])|([\Q$-_.+\!*'(),;:@&=\E]))*)(([\Q/\\E])*((%[0-9a-fA-F]{2})|([a-zA-Z0-9])|([\Q$-_.+\!*'(),;:@&=\E]))*)*)(\?((%[0-9a-fA-F]{2})|([a-zA-Z0-9])|([\Q$-_.+!*'(),;:@&=<>#"{}[] ^`~|\/\E]))*)*)*)

p = r'''((((ftp:|https:|http:)([\Q/\\E])*)|())(((%[0-9a-fA-F][0-9a-fA-F])|([a-zA-Z0-9])|([\Q$-_.+!*'(),;?&=\E]))+(:((%[0-9a-fA-F][0-9a-fA-F])|([a-zA-Z0-9])|([\Q$-_.+!*'(),;?&=\E]))*)?@)?(((((([a-zA-Z0-9]){1}([a-zA-Z0-9\-])*([a-zA-Z0-9]{1}))|([a-zA-Z0-9]))\.)+(biz|com|edu|gov|info|int|mil|name|net|org|pro|aero|cat|coop|jobs|museum|travel|arpa|root|mobi|post|tel|asia|geo|kid|mail|sco|web|xxx|nato|example|invalid|test|bitnet|csnet|onion|uucp|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cu|cv|cx|cy|cz|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|st|su|sv|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|um|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw))|([0-9]{1,3}(\.[0-9]{1,3}){3}))(\:([0-9]+))?(([\Q/\\E])+((((%[0-9a-fA-F][0-9a-fA-F])|([a-zA-Z0-9])|([\Q$-_.+\!*'(),;:@&=\E]))*)(([\Q/\\E])*((%[0-9a-fA-F]{2})|([a-zA-Z0-9])|([\Q$-_.+\!*'(),;:@&=\E]))*)*)(\?((%[0-9a-fA-F]{2})|([a-zA-Z0-9])|([\Q$-_.+!*'(),;:@&=<>#"{}[] ^`~|\/\E]))*)*)*)'''

def regex():
    print re.findall(p,ss)
    return re.findall(p,ss)

def comp():
	pattern = re.compile(p)
	print pattern.findall(ss)
	return pattern.findall(ss)

print '分词器耗时:', timeit(stmt=tokenize,number= 1)
print '正则耗时:', timeit(stmt=regex,number= 1)
print '编译后正则耗时:', timeit(stmt=comp,number= 1)