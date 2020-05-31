# _*_coding:utf-8_*_
"""
为项目插入初始化数据
Author: Lingren Kong
Created Time: 2020/5/31 20:56
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

def randUser(n):
    """
    随机生成一些学生信息到数据库
    预先准备了一些随机的姓名在Sname文件里面
    :return:
    """
    from numpy.random import randint
    head = 2018200000
    t = 0
    s = 0
    with open("Sname.txt",'r',encoding='utf8') as f:
        for _ in range(n):
            # 每次读取3个字符（准备的都是三个字的名字）
            name = f.read(3)
            # 如果没有读到数据，跳出循环
            if not name:
                break
            r = randint(0,20)
            if r>17:#随机设置一部分作为老师
                t += 1
                id = 'T'+str(head+t)
                type = '教师'
            else:
                s += 1
                id = 'S' + str(head + s)
                type = '学生'
            password = id #默认密码
            get = 0
            restrict = 0
            cursor = get_cursor()
            cr = cursor.execute(
                f"INSERT INTO Userlist VALUES ('{id}','{name}','{password}','{type}',{get},NULL,{restrict})"
            )
            # 备注设为空
            cr.commit()#不提交不行的
            print(cr.rowcount) #影响的行数，检查是不是有效操作

if __name__ == '__main__':
    randUser(200)
