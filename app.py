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






if __name__ == '__main__':
    app.run(debug=True)
