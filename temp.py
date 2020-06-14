# _*_coding:utf-8_*_
"""
Author: Lingren Kong
Created Time: 2020/6/14 17:31
"""

import datetime
a = datetime.datetime.strptime('2020-06-01','%Y-%m-%d')
print(a)
(a+datetime.timedelta(21)).strftime('%Y-%m-%d')

import json
b = [2.5,3.6]
json.dumps(b)