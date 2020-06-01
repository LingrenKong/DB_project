from flask import Flask
from flask import Response, request, render_template_string,  redirect, Blueprint,render_template,send_file
#画图功能
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure

app = Flask(__name__)

#from flask.ext.bootstrap import Bootstrap
#Bootstrap(app)  # 把程序实例即 app 传入构造方法进行初始化

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
    return render_template('index.html')

@app.route('/boostrap_demo/')
def try_boostrap():
    return render_template('base.html')

@app.route('/admin/')
def admin():
    return render_template('admin.html')

@app.route('/admin/summary/')
def book_summary():
    cursor = get_cursor()
    exist = cursor.execute("SELECT * FROM book WHERE removed=0").fetchall()
    cursor = get_cursor()
    removed = cursor.execute("SELECT * FROM book WHERE removed=1").fetchall()
    return render_template('book_summary.html',exist = exist,removed=removed)

if __name__ == '__main__':
    app.run(debug=True)
