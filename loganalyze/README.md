# Logparser  

本项目使用IPLoM对日志进行解析，原项目为https://github.com/logpai/logparser。之所以使用IPLoM，是因为IPLoM对于大部分种类日志的分析正确率均较高。比对结果见https://logparser.readthedocs.io/en/latest/benchmark.html。


## 相关依赖
- python
- scipy
- numpy
- scikit-learn
- pandas
- polyglot

## 项目结构
- benchmark：对于不同种类日志的最佳参数配置

- demo：主程序

- logparser：IPLoM分析器

- logs：存放日志

## 使用方法

### 解析日志并结构化（此部分必须用python2，否则会有bug）

1. 将要分析的日志放入logs文件夹中
2. 打开demo/parselog.py，需要传入两个参数：
	- --logname：日志文件名
	- --pattern：日志的格式
示例：parselog.py --logname=cart1.log --pattern="<A> <B>  <C> <D> <E> <F> : <Content>"
3. 运行IPLoM.py，结果存放在demo/IPLoM_result

#### Java调用方法
建议使用jython方法（其他方法也可），调用时需要传入两个参数--logname以及--pattern，详见使用方法第二步。  
日志格式提取方法：随便提取某一行日志，将其中的文字依次替换。（最后一个<>里的内容必须为Content）
示例：
某一行内容为：2019-11-01 07:00:26.245  INFO [bootstrap,,,] 6 --- [           main] s.c.a.AnnotationConfigApplicationContext : Refreshing org.springframework.context.annotation.AnnotationConfigApplicationContext@51521cc1: startup date [Fri Nov 01 07:00:26 GMT 2019]; root of context hierarchy
依次替换为：<A> <B>  <C> <D> <E> <F> : <Content>

### 构建工作流
workflow.py即可,生成vectorize,newvectorize.txt,new2vectorize.txt

注：以下部分均为python3环境,结果存放在IPLoM_result
### 分析实体(需要polyglot)
直接运行parseentity.py即可,生成entitydata.json用于进行关系提取，生成entityandarrtibute.csv用于记录实体与属性。
注：使用pycharm运行的时候可能出现polyglot乱码的情况，此时重启pycharm即可解决。

### 生成最终json文件以传给后端使用
直接运行getjson.py即可，生成data.json，传给后端
