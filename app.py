from flask import Flask
from flask import Response, request, render_template_string,  redirect, Blueprint,render_template,send_file
#画图功能
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure

app = Flask(__name__)


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



@app.route('/')
def hello_world():
    return 'Hello World!'

def randStu(n):
    """
    随机生成一些(n)学生信息到数据库
    预先准备了一些随机的姓名在Sname里面
    :return:
    """
    head = 2018200000
    with open("Sname.txt",'r',encoding='utf8') as f:
        for i in range(n):
            # 每次读取3个字符（准备的都是三个字的名字）
            Sname = f.read(3)
            # 如果没有读到数据，跳出循环
            if not Sname:
                break
            Sno = str(head+i)
            password = Sno #暂时先这样
            max = 10
            take = 0
            rest = 10
            cursor = get_cursor()
            cr = cursor.execute(
                f"INSERT INTO Stu VALUES ('{Sno}','{Sname}','{password}',{max},{take},{rest})"
            )
            cr.commit()#不提交不行的
            print(cr.rowcount)#影响的行数

randStu(10)

cursor = get_cursor()
t = cursor.execute("SELECT * FROM STU")
for i in t:
    print(i)



if __name__ == '__main__':
    app.run(debug=True)
