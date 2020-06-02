from flask import Flask, session
from flask import Response, request, render_template_string,  redirect, Blueprint,render_template,send_file
#画图功能
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure

app = Flask(__name__)
app.config["SECRET_KEY"] = "klr"#设置一个key才可以有session，否则session是none
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

@app.route('/boostrap-demo/')
def try_boostrap():
    return render_template('base.html')

@app.route('/admin/')
def admin():
    return render_template('admin.html')

@app.route('/admin/book-summary/')
def book_summary():
    cursor = get_cursor()
    exist = cursor.execute("SELECT * FROM book WHERE removed=0").fetchall()
    cursor = get_cursor()
    removed = cursor.execute("SELECT * FROM book WHERE removed=1").fetchall()
    return render_template('book_summary.html',exist = exist,removed=removed)

@app.route('/user-control/',methods = ['POST', 'GET'])
def user():
    mode = None
    cursor = get_cursor()
    if request.method == 'GET':
        mode = 1
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        result = cursor.execute(f"SELECT * FROM Userlist WHERE Urestrict=0 AND id='{id}' AND Upassword='{password}' ")
        if result.fetchone():
            mode = 2 #登录有效
            session['user_id'] = id#后面都可以使用了
        else:
            mode = 3
            session['user_id'] = None
    return render_template('user.html',mode=mode)

@app.route('/user-control/search/',methods = ['POST', 'GET'])
def book_search():
    # 这个搜索不需要登录要求
    search = None
    cursor = get_cursor()
    if request.method == 'POST':
        form = request.form
        search = cursor.execute(f"SELECT * FROM book WHERE removed=0 AND Bname LIKE '%{form.get('Bname')}%'")
    return render_template('book_search.html',search=search)

@app.route('/user-control/borrow/',methods = ['POST', 'GET'])
def book_borrow():
    # 借阅需要登录
    ISBN = None
    cursor = get_cursor()
    print(session.get('user_id'))
    if not session.get('user_id') or session['user_id']==None:
        #print(session.get('user_id'))
        return redirect('/user-control/')
    return render_template('book_borrow.html',id=session.get('user_id'))

if __name__ == '__main__':
    app.run(debug=True)
