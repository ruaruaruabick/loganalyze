#!/usr/bin/env python
# -*- coding:utf-8 -*-

import math
import sys
import getopt
import pandas as pd
import json
#解析日志并结构化
sys.path.append('../')
reload(sys)
sys.setdefaultencoding("utf-8")
from logparser import IPLoM

name = ""
options,args = getopt.getopt(sys.argv[1:],[],["logname=","pattern="])
input_dir    = '../logs/'  # The input directory of log file
output_dir   = 'IPLoM_result/'  # The output directory of parsing results
log_file     = options[0][1]  # The input log file name
log_format   = options[1][1].lstrip('\"').rstrip('\"') # HDFS log format
maxEventLen  = 500  # The maximal token number of log messages (default: 200)
step2Support = 0  # The minimal support for creating a new partition (default: 0)
CT           = 0.35  # The cluster goodness threshold (default: 0.35)
lowerBound   = 0.25  # The lower bound distance (default: 0.25)
upperBound   = 0.9  # The upper bound distance (default: 0.9)
regex        = []  # Regular expression list for optional preprocessing (default: [])

parser = IPLoM.LogParser(log_format=log_format, indir=input_dir, outdir=output_dir,
                         maxEventLen=maxEventLen, step2Support=step2Support, CT=CT, 
                         lowerBound=lowerBound, upperBound=upperBound, rex=regex)
parser.parse(log_file)

