# _*_coding:utf-8_*_
"""
Author: Lingren Kong
Created Time: 2020/5/31 21:05
"""

#数据库配置
import pyodbc
server = 'localhost'
database = 'mydatabase'
username = 'learn'#一般用的是sa
password = 'sqlpassword'#自己的密码

def get_cursor():
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server
        + ';DATABASE=' + database + ';UID=' + username + ';PWD='
        + password + ';CHARSET=GBK;Trusted_Connection=yes;')
    # Trusted_Connection=yes;可能需要
    cursor = cnxn.cursor()
    return cursor



def load_book(path):
    import pandas as pd
    import re
    from numpy.random import randint
    books = pd.read_csv(path,index_col=None)
    cursor = get_cursor()
    for i in range(len(books)):
        row = books.iloc[i]
        id = row['书号']
        Bname = row['书名']
        brief = row['摘要']
        Btype = row['类别']
        author = row['作者']
        Press = row['出版社']
        price = re.search(r'\d+\.\d*',row['价格']).group()#清洗数据
        num = randint(10,200)
        removed = 0
        try:
            cursor.execute(
                f"INSERT INTO Book VALUES ('{id}','{Bname}','{brief}','{Btype}','{author}','{Press}',{price}, {num}, NULL, 0)"
            )# 备注为NULL，书被删除设置为0（否）
            cursor.execute(
                f"INSERT INTO BAlter VALUES ('{id}','Admin000','2020-05-01','新书入库','{num}',0,'{num}','5月1日由管理员导入初始图书数据')"
            )
            cursor.commit()
        except:
            print(f"INSERT INTO book VALUES ('{id}','{Bname}','{brief}','{Btype}','{author}','{Press}',{price}, {num}, NULL, 0)")
            print(f"INSERT INTO BAlter VALUES ('{id}','Admin000','2020-05-01','{num}',0,'{num}','5月1日由管理员导入初始图书数据')")
            print('上面一句有问题')


load_book('books.csv')