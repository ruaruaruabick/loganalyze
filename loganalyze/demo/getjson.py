import math
import sys
import getopt
import pandas as pd
import json

#生成json文件
class enetityjson():
    def __init__(self,name,attribute):
        self.name = name
        self.attribute = attribute

class relationjson():
    def __init__(self,relation):
        self.name = relation['relation']
        self.entities = [relation['entity1']]
        if 'entity2' in relation.keys():
            self.entities.append(relation['entity2'])

class patternjson():
    def __init__(self,patternid,logkey,content,entities,relation):
        self.patternid =patternid
        self.logkey = logkey
        self.content = content
        self.entities = entities
        self.relation = relation

class transactionjson():
    def __init__(self):
        self.patternlist = []
    def addpattern(self,pattern):
        self.patternlist.append(pattern)

class workflowjson():
    def __init__(self,name,lastflow,nextflow):
        self.name = name
        self.lastflow = lastflow
        self.nextflow = nextflow
        self.transactionlist = []
    def addtrans(self,trans):
        self.transactionlist.append(trans)
    def setlast(self,last):
        self.lastflow = last
    def setnext(self,next):
        self.nextflow = next
#读入pattern
#logkeyfile=命令行
patternlist = []
workflowlist = []
data = pd.read_csv("IPLoM_result/cart1.log_LogKey.csv")
for row in data.iterrows():
    row = row[1]
    key = int(row['LogKey'])
    patternlist.append(patternjson(row["patternid"],key,row["pattern"],[],"relation").__dict__)
#读入实体
with open('IPLoM_result/entitydata.json','r') as f:
    relation = json.loads(f.read())
    for i in range(len(relation)):
        for en in relation['sent' + str(i + 1)]['entities']:
            patternlist[i]['entities'].append(enetityjson(en['name'],en['attributes']).__dict__)
#读入关系json
with open('IPLoM_result/relation.json','r') as f:
    relation = json.loads(f.read())
    #构建每个pattern的关系，并保存在字典中
    for i in range(len(relation)):
        index = i+1
        patternlist[i]['relation'] = relationjson(relation['sent'+str(index)]).__dict__
linenow = 0
#按行读取logkey
for line in open("IPLoM_result/newvectorize.txt"):
    key_list = line.split(" ")
    lk = []
    for key in key_list:
        key = int(key)
        if key > 1000:
            key1 = int(key/1000)
            key2 = key-key1*1000
            if key1 not in lk:
                lk.append(key1)
            if key2 not in lk:
                lk.append(key2)
        else:
            if key not in lk:
                lk.append(key)
    #构建transaction，lk为某transaction的logkey序列
    temptrans = transactionjson()
    for key in lk:
        temptrans.addpattern(patternlist[key-1])
    #构建workflow
    name = "workflow"+str(linenow)
    tempflow = workflowjson(name,"la","ne")
    tempflow.addtrans(temptrans.__dict__)
    workflowlist.append(tempflow.__dict__)
    linenow = linenow+1
#构建前置后置
for num in range(len(workflowlist)):
    workflowlist[num]["lastflow"] = "workflow" + str(num - 1)
    workflowlist[num]["nextflow"] = "workflow" + str(num + 1)
    if num == 0:
        workflowlist[num]["lastflow"] ="none"
    if num == len(workflowlist)-1:
        workflowlist[num]["nextflow"] ="none"

#写入json
with open('IPLoM_result/data.json', 'w') as fw:
    json.dump(workflowlist,fp=fw)
