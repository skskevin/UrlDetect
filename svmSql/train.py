#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-10-25 14:41:22
# @Author  : dongchuan
# @Version : v1.0
# @Desc    : SVM模型训练#
#参数长度
# 信息熵
# 是否包含sql关键字
# 关键字个数
import re
import sys
import math
import numpy as np
from sklearn import svm
from sklearn import metrics
from collections import Counter
from sklearn.model_selection._split import train_test_split
from sklearn.externals import joblib

from setenv import *

import warnings
warnings.filterwarnings("ignore")



def entropy(s):
    p, lns = Counter(s), float(len(s))
    return -sum( count/lns * math.log(count/lns, 2) for count in p.values())


def clean(data):
    data = data.lower()
    # 删除word中的空白符
    data = re.sub(r'(\r|\n|\t)+', ' ', data)
    # \0阶段符号替换
    data = re.sub(r'\\0', "", data)
    data = re.sub(r'-{2,}', " ", data)
    # 干掉注释/**/
    data = re.sub(r'\/\*.?\*\/', " ", data)
    data = re.sub(r'\/\*', "", data)

    return data

def genvec(sow, words):
    vecs = []
    if not words:
        vecs = [[-1]]
    for word in words:
        if word in sow:
            vecs.append([sow[word]])
        else:
            vecs.append([-1])

    return np.array(vecs)

def _type(d):
    _types = {'normal': 1, 'abnormal': 0}
    return _types[d]


if __name__ == '__main__':
    # with open("good.txt") as f:
    #     for line in f:
    #         line = clean(line)
    #         length = len(line)
    #         parser = SQLTokenizer()
    #         parser.sqlRunParser(line)
    #         words = parser.get_words()
    #         keyCount = len(words)
    #         if keyCount:
    #            flag = 1
    #         else:
    #            flag = 0
    #         enpy = entropy(line)
            # print length, keyCount,flag,enpy,'normal'

    data = np.loadtxt("sample.txt", delimiter=' ', converters={4: _type})

    x, y = np.split(data, (4,), axis=1)

    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=1, train_size=0.8)

    clf = svm.SVC(C=30, kernel='rbf', gamma=2.5, decision_function_shape='ovr')
    rf = clf.fit(x_train, y_train.ravel())

    joblib.dump(rf, 'rf.model')  # 保存模型文件

    print "训练集正确率:", clf.score(x_train, y_train)  # 训练集正确率
    print "测试集正确率:", clf.score(x_test, y_test)  # 测试集正确率
