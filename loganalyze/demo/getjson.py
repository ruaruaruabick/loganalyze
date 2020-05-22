import math
import sys
import getopt
import pandas as pd
import json

#
def parsepa(patter,eanda):
    for i in eanda:
        if i == '\n' and len(eanda) == 1:
            for j in range(len(patter['entities'])):
                patter['entities'][j]['attribute'] = []
        else:
            if i == '\n':
                continue
            entity, att = i.split(',')
            for j in range(len(patter['entities'])):
                if entity in patter['entities'][j].values():
                    patter['entities'][j]['attribute'] = [att]
                    break
    return patter
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
        newpa = patternjson(pattern["patternid"],pattern["logkey"],pattern["content"],pattern["entities"],pattern["relation"])
        self.patternlist.append(newpa.__dict__)

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
tempae = open("IPLoM_result/attlist","r")
allworkflow = open("IPLoM_result/new2vectorize.txt")
#按行读取logkey
for line in open("IPLoM_result/newvectorize.txt"):
    line1 = allworkflow.readline()
    key_list = line.split(" ")
    key_list1 = line1.split(" ")
    lk = []
    lk1 = []
    for key in key_list:
        key = int(key)
        if key > 1000:
            key1 = int(key/1000)
            key2 = key-key1*1000
            lk.append(key1)
            lk.append(key2)
        else:
            lk.append(key)
    for key in key_list1:
        key = int(key)
        if key > 1000:
            key1 = int(key / 1000)
            key2 = key - key1 * 1000
            lk1.append(key1)
            lk1.append(key2)
        else:
            lk1.append(key)
    #构建transaction，lk为某transaction的logkey序列
    temptrans = transactionjson()
    count = 0
    count1 = 0
    while count < len(lk):
        key = lk[count]
        if lk[count] == lk1[count1]:
            temppattern = patternlist[key-1]
            tempaae = tempae.readline()
            templist = tempaae.split(" ")
            tempentity = patternlist[key - 1]['entities']
            newpa = patternjson(patternlist[key - 1]['patternid'], patternlist[key - 1]['logkey'], patternlist[key - 1]['content'],
                        tempentity, patternlist[key - 1]['relation']).__dict__
            temptrans.addpattern(parsepa(newpa,templist))
        #处理循环
        else:
            rekey = int(-lk1[count1] / 1000)
            relength = -(key * 1000+lk1[count1])
            relist = []
            for temp in range(relength):
                temppattern = patternlist[key - 1]
                tempaae = tempae.readline()
                templist = tempaae.split(" ")
                tempentity = patternlist[key - 1]['entities']
                newpa = patternjson(patternlist[key - 1]['patternid'], patternlist[key - 1]['logkey'],
                                    patternlist[key - 1]['content'],
                                    tempentity, patternlist[key - 1]['relation']).__dict__
                temptrans.addpattern(parsepa(newpa, templist))
                relist.append(lk[count])
                count = count + 1
                key = lk[count]
            while True:
                tempp = True
                tempcount = count
                for i in relist:
                    if count == len(lk):
                        tempp = False
                        break
                    elif lk[count] != i:
                        tempp = False
                        count = tempcount - 1
                        break
                    else:
                        count = count +1
                if tempp == False:
                    break
        count = count + 1
        count1 = count1 + 1
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
