#!/usr/bin/python
# -*- coding:utf8 -*-

from polyglot.detect import Detector
from polyglot.text import Text
import os
import pandas as pd
import string
import json
import sys
import re
sys.path.append('IPLoM_result/')
sys.path.append('../logs')
reg = "[^0-9A-Za-z\u4e00-\u9fa5]"
#将字典按值排序
def sort_by_value(d):
    newdict = {}
    items=d.items()
    backitems=[[v[1],v[0]] for v in items]
    backitems.sort(reverse=True)
    for v in backitems:
        newdict[v[1]] = v[0]
    return newdict

#提取实体
result = os.popen("polyglot  --lang en  ner --input ../logs/cart1.log").readlines()
#result = os.popen("polyglot  --lang en  ner --input ../logs/HDFS_2k.log").readlines()
newresult = []
numers = {}
for line in result:
    myentity = line[0:len(line)-6]
    if len(myentity) > 2 :
        mypos = Text(myentity,hint_language_code='en').pos_tags
        for pos in mypos:
            if 'ADP' not in pos and 'POS' not in pos and 'PUNCT' not in pos and 'INTJ' not in pos and 'VERB' not in pos and 'SYM' not in pos:
                if pos[0] not in newresult:
                    newresult.append(pos[0])
                    numers[str(pos[0])] = 1
                else :
                    numers[str(pos[0])] = numers[str(pos[0])]+1
"""
newresult：可能的实体
numers：可能的实体出现的次数
ExistEntity：LogKey中存在的实体
ExistEntityDict：LogKey中存在的实体按出现次数排序
"""
#查看提取出的实体是否在Logkey中
punc = string.punctuation
LogKeyFile = pd.read_csv('IPLoM_result/cart1.log_templates.csv')
#LogKeyFile = pd.read_csv('IPLoM_result/HDFS_2k.log_templates.csv')
LogKey = LogKeyFile['EventTemplate'].tolist()
LogKeyStr = "".join(LogKey)
ExistEntity = []
ExistEntityDict = {}
for entity in newresult:
    if entity in LogKeyStr and entity != 'at' and entity != 'in' and entity != 'for' and entity != 'to' and entity!= 'of':
        mypos = Text(entity, hint_language_code='en').pos_tags
        if 'ADV' != mypos[0][1] and 'ADJ' != mypos[0][1] and 'NUM' != mypos[0][1] and 'PUNCT' != mypos[0][1] and str(mypos[0][0]) not in punc and not str(mypos[0][0]).isdigit():
            ExistEntity.append(entity)
            ExistEntityDict[str(entity)] = numers[str(entity)]
ExistEntityDict = sort_by_value(ExistEntityDict)

#将logkey与实体对应起来
keyentitydict = {}
for log in LogKey:
    keyentitydict[log] = []
    for key in ExistEntityDict.keys():
        if key in log.split(" "):
            keyentitydict[log].append(key)

#读取日志，提取参数
logcsv = pd.read_csv('IPLoM_result/cart1.log_structured.csv')
#logcsv = pd.read_csv('IPLoM_result/HDFS_2k.log_structured.csv')
ep = pd.DataFrame(logcsv,columns=['EventTemplate','ParameterList'])
entityparaposs = {}
entitypara = {}
for i in ExistEntityDict.keys():
    entityparaposs[i] = 0
    entitypara[i] = []
#计算实体有参数的可能性
for index, row in ep.iterrows():
    if row['ParameterList'] == '[]':
        for entity in keyentitydict[row['EventTemplate']]:
            entityparaposs[entity] = entityparaposs[entity] - 1
    else:
        for entity in keyentitydict[row['EventTemplate']]:
            entityparaposs[entity] = entityparaposs[entity] + 1
entityparaposs = sort_by_value(entityparaposs)
#将参数与实体对应起来
tempf = open('IPLoM_result/attlist','w')
#tempf = open('IPLoM_result/HDFSattlist','w')

for index, row in ep.iterrows():
    seque = []
    if not row['ParameterList'] == '[]':
        para = row['ParameterList'].split(',')
        #找出有参数的实体
        for j in keyentitydict[row['EventTemplate']]:
            if len(seque) == 2:
                if entityparaposs[j] >  entityparaposs[seque[1]]:
                    seque.pop(0)
                    seque.append(j)
            else:
                seque.append(j)
        for j in range(min(len(para),len(seque))):
            para[j] = re.sub(reg, '', para[j])
            entitypara[seque[j]] = para[j]
            tempf.write(seque[j]+','+para[j]+' ')
    tempf.write('\n')
tempf.close()
#保存实体与属性
keys = list(entitypara.keys())
items = list(entitypara.items())
item = []
for i in items:
    if type(i[1]) == str:
        temps = i[1]
        item.append(temps)
    else:
        item.append(i[1])
eadf = pd.DataFrame({'entity':keys,'attribute':item})
eadf.to_csv("./IPLoM_result/entityandattribute.csv",index=False)
#eadf.to_csv("./IPLoM_result/HDFSentityandattribute.csv",index=False)
#生成entityjson
class sentc():
    def __init__(self,content,entities):
        self.content = content
        self.entities = entities
class entityc():
    def __init__(self,name,start,end,attributes):
        self.name = name
        self.start = start
        self.end = end
        if type(attributes) == str:
            self.attributes = [attributes]
        else:
            self.attributes = attributes


sentlist = {}
tempint = 1
for log in LogKey:
    entitylist = []
    for entity in keyentitydict[log]:
        start = log.find(entity)
        end = start + len(entity)-1
        entitylist.append(entityc(entity,start,end,entitypara[entity]).__dict__)
    sentlist["sent"+str(tempint)] = sentc(log,entitylist).__dict__
    tempint =tempint + 1
with open('IPLoM_result/entitydata.json', 'w') as fw:
#with open('IPLoM_result/HDFSentitydata.json', 'w') as fw:
    json.dump(sentlist,fp=fw)
