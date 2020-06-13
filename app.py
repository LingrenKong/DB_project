from flask import Flask, session
from flask import Response, request, render_template_string,  redirect, Blueprint,render_template,send_file,url_for
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

def get_md5(raw):
    from hashlib import md5
    obj = md5(raw.encode(encoding='utf-8'))
    return obj.hexdigest()

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/boostrap-demo/')
def try_boostrap():
    return render_template('base.html')

# admin部分

@app.route('/admin/')
def admin():
    login = False
    error = request.args.get("error")
    if session.get('admin_id'):
        login = True
    return render_template('admin.html',login=login,error=error,Ano=session.get('admin_id'),Atype=session.get('Atype'),Amore=session.get('Amore'))

@app.route('/admin/login/',methods = ['POST'])
def admin_login():
    Ano = request.form['id']
    password = get_md5(request.form['password'])
    print(password)
    cursor = get_cursor()
    result = cursor.execute(f"SELECT * FROM AdminList WHERE Ano='{Ano}' AND Apassword='{password}' ")
    data =  result.fetchone()
    print(data)
    if data:
        session['admin_id'] = Ano  # 后面都可以使用了
        session['Atype']=data[2]
        session['Amore']=data[3]
        return redirect(url_for('admin'))
    else :
        return redirect(url_for('admin',error=True))

@app.route('/admin/logout/',methods = ['POST'])
def admin_logout():
    session['admin_id'] = None
    session['Aname'] = None
    session['Atype'] = None
    return redirect('/admin/')

@app.route('/admin/book-summary/')
def book_summary():
    cursor = get_cursor()
    exist = cursor.execute("SELECT * FROM book WHERE removed=0").fetchall()
    cursor = get_cursor()
    removed = cursor.execute("SELECT * FROM book WHERE removed=1").fetchall()
    return render_template('book_summary.html',exist = exist,removed=removed)

# user部分

@app.route('/user/',methods = ['POST', 'GET'])
def user():
    login = False
    error = request.args.get("error")
    if session.get('user_id'):
        login = True
    return render_template('user.html',login=login,error=error,Uname=session.get('Uname'),Utype=session.get('Utype'),Urestrict=session.get('Urestrict'))

@app.route('/user/login/',methods = ['POST'])
def uer_login():
    Uno = request.form['id']
    password = get_md5(request.form['password'])
    print(password)
    cursor = get_cursor()
    result = cursor.execute(f"SELECT * FROM Userlist WHERE Uno='{Uno}' AND Upassword='{password}' ")#Urestrict=0 AND
    data =  result.fetchone()
    print(data)
    if data:
        session['user_id'] = Uno  # 后面都可以使用了
        session['Uname']=data[1]
        session['Utype']=data[3]
        session['Urestrict']=data[6]
        return redirect(url_for('user'))
    else :
        return redirect(url_for('user',error=True))

@app.route('/user/logout/',methods = ['POST'])
def user_logout():
    session['user_id'] = None
    session['Uname'] = None
    session['Utype'] = None
    session['Urestrict'] = None
    return redirect('/user/')

@app.route('/user/signup/',methods = ['POST', 'GET'])
def user_signup():
    if request.method=='POST':
        cursor = get_cursor()
        Uname = request.form['name']
        Uno = 'U'+request.form['id']
        Upassword = get_md5(request.form['password'])
        date = request.form['date']
        print(date)
        cursor.execute(f"INSERT INTO UserList VALUES ('{Uno}','{Uname}','{Upassword}','校外用户',0,NULL,1)")
        cursor.execute(f"INSERT INTO UAlter VALUES ('{Uno}','Admin003','{date}','校外注册',NULL)")
        cursor.commit()
        return redirect(url_for('user'))
    return render_template('user_signup.html')


@app.route('/user/search/',methods = ['POST', 'GET'])
def book_search():
    # 这个搜索不需要登录要求
    search = None
    cursor = get_cursor()
    if request.method == 'POST':
        form = request.form
        search = cursor.execute(f"SELECT * FROM book WHERE removed=0 AND Bname LIKE '%{form.get('Bname')}%'")
    return render_template('book_search.html',search=search)

@app.route('/user/borrow/',methods = ['POST', 'GET'])
def book_borrow():
    # 借阅需要登录
    ISBN = None
    cursor = get_cursor()
    print(session.get('user_id'))
    if not session.get('user_id') or session['user_id']==None:
        #print(session.get('user_id'))
        return redirect('/user/')
    return render_template('book_borrow.html',id=session.get('user_id'))

if __name__ == '__main__':
    app.run(debug=True)
