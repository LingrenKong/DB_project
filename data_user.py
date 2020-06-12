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

def get_md5(raw):
    from hashlib import md5
    obj = md5(raw.encode(encoding='utf-8'))
    return obj.hexdigest()

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
            password = get_md5(id) #默认密码
            get = 0
            restrict = 0
            cursor = get_cursor()
            cr = cursor.execute(
                f"INSERT INTO UserList VALUES ('{id}','{name}','{password}','{type}',{get},NULL,{restrict})"
            )
            cr = cursor.execute(#假装是5月1日导入
                f"INSERT INTO UAlter VALUES ('{id}','Admin000','2020-05-01','创建账户','5月1日由管理员导入学生教师账户数据')"
            )
            # 备注设为空
            cr.commit()#不提交不行的
            print(cr.rowcount) #影响的行数，检查是不是有效操作

def initAdmin():
    cursor = get_cursor()
    #密码是用户名加密
    cr = cursor.execute("INSERT INTO AdminList VALUES \
                        ('Admin000','b0dc5be3a5ac529022294740086a4725','超级管理','这是初始创建的超级管理员，可以有所有操作权限')")
    cr = cursor.execute("INSERT INTO AdminList VALUES \
                        ('Admin001','55772918a13bc70691fca45668c4e353','图书管理','这是初始创建的图书管理员，可以管理图书的数据')")
    cr = cursor.execute("INSERT INTO AdminList VALUES \
                        ('Admin002','09068795b03102a1688425253514f63f','临时权限','这是初始创建的临时权限，只可以用于解禁学生欠费')")
    cr = cursor.execute("INSERT INTO AdminList VALUES \
                        ('Admin003','491a7ae532f8c8e4b8811e77a80bb6ee','学生管理','这是初始创建的学生管理员，可以管理学生')")
    cr.commit()

if __name__ == '__main__':
    #initAdmin()
    randUser(200)
