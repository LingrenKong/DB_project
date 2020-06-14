from flask import Flask, session
from flask import Response, request, render_template_string,  redirect, Blueprint,render_template,send_file,flash,url_for

#画图功能
#from matplotlib.backends.backend_agg import FigureCanvasAgg
#from matplotlib.backends.backend_svg import FigureCanvasSVG
#from matplotlib.figure import Figure
import json
import datetime


app = Flask(__name__)
app.config["SECRET_KEY"] = "klr"#设置一个key才可以有session，否则session是none
#from flask.ext.bootstrap import Bootstrap
#Bootstrap(app)  # 把程序实例即 app 传入构造方法进行初始化

#数据库配置
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

@app.route('/admin/book-control/')
def book_summary():
    if session.get('admin_id')==None or session['Atype'] not in ['超级管理','图书管理']:
        return redirect('/admin/')
    cursor = get_cursor()
    exist = cursor.execute("SELECT * FROM book WHERE removed=0").fetchall()
    cursor = get_cursor()
    removed = cursor.execute("SELECT * FROM book WHERE removed=1").fetchall()
    return render_template('admin_book.html',exist = exist,removed=removed)

@app.route('/admin/book-control/add/',methods=['POST','GET'])
def admin_book_add():
    if session.get('admin_id')==None or session['Atype'] not in ['超级管理','图书管理']:
        return redirect('/admin/')
    if request.method =='GET':
        return render_template('admin_book_add.html')
    else:
        Ano = session['admin_id']
        Bno = request.form['ISBN']
        Bname = request.form['Bname']
        brief = request.form['brief']
        Btype = request.form['Btype']
        author = request.form['author']
        Press = request.form['Press']
        price = request.form['price']
        num = request.form['num']
        date = request.form['date']
        sql1 = f"INSERT INTO Book VALUES ('{Bno}','{Bname}','{brief}','{Btype}','{author}','{Press}',{price},{num},'在{date}购入此书共计{num}本,由{Ano}进行操作',0)"
        sql2 = f"INSERT INTO BAlter VALUES ('{Bno}','{Ano}','{date}','新书入库',{num},0,{num},'在{date}购入此书共计{num}本,由{Ano}进行操作')"
        print(sql1,sql2)
        cursor = get_cursor()
        cursor.execute(sql1)
        cursor.execute(sql2)
        cursor.commit()
        redirect('/admin/book-control/add/')

@app.route('/admin/book-control/remove/',methods=['POST'])
def admin_book_remove():
    Ano = session['admin_id']
    Bno = request.form['ISBN']
    date = request.form['date']
    num = request.form['num']
    sql1 = f"UPDATE Book SET removed=1, num=0 WHERE Bno='{Bno}'"
    sql2 = f"INSERT INTO BAlter VALUES ('{Bno}','{Ano}','{date}','图书出库',{num},{num},0,'在{date}下架{num}本,由{Ano}进行操作')"
    print(sql1,sql2)
    cursor = get_cursor()
    cursor.execute(sql1)
    cursor.execute(sql2)
    cursor.commit()
    redirect('/admin/book-control/')

@app.route('/admin/book-control/reset/',methods=['POST'])
def admin_book_reset():
    Ano = session['admin_id']
    Bno = request.form['ISBN']
    date = request.form['date']
    num = request.form['num']
    sql1 = f"UPDATE Book SET removed=0,num={num} WHERE Bno='{Bno}'"
    sql2 = f"INSERT INTO BAlter VALUES ('{Bno}','{Ano}','{date}','图书重新上架',{num},0,{num},'在{date}将书重新上架{num}本,由{Ano}进行操作')"
    print(sql1,sql2)
    cursor = get_cursor()
    cursor.execute(sql1)
    cursor.execute(sql2)
    cursor.commit()
    redirect('/admin/book-control/')

@app.route('/admin/user-control/')
def free_user():
    if session.get('admin_id')==None or session['Atype'] not in ['超级管理','用户管理']:
        return redirect('/admin/')
    cursor = get_cursor()
    restricted = cursor.execute("SELECT * FROM UserList WHERE Urestrict=1").fetchall()
    print('restricted:',restricted)
    s = cursor.execute("SELECT COUNT(*) FROM UserLIst WHERE Utype='学生'").fetchone()[0]
    t = cursor.execute("SELECT COUNT(*) FROM UserLIst WHERE Utype='教师'").fetchone()[0]
    u = cursor.execute("SELECT COUNT(*) FROM UserLIst WHERE Utype='校外用户'").fetchone()[0]
    print(s,t,u)
    data = [s,t,u]
    return render_template('admin_user.html',restricted=restricted,chart1=data)

@app.route('/admin/user-control/restrict/',methods=['POST'])
def admin_user_restrict():
    if session.get('admin_id')==None or session['Atype'] not in ['超级管理','用户管理']:
        return redirect('/admin/')
    Ano = session['admin_id']
    date = request.form['date']
    t = datetime.datetime.strptime(date,'%Y-%m-%d')
    t = t-datetime.timedelta(21)
    checkDate = t.strftime('%Y-%m-%d')
    cursor = get_cursor()
    sql = f"SELECT DISTINCT Uno FROM Borrow WHERE outDate<'{checkDate}'"
    print(sql)
    Unos = cursor.execute(sql).fetchall()
    for one in Unos:
        Uno = one[0]
        sql1 = f"INSERT INTO UAlter VALUES ('{Uno}','{Ano}','{date}','封号','超时未还书就封号')"
        sql2 = f"UPDATE UserList SET Urestrict=1 WHERE Uno='{Uno}'"
        cursor.execute(sql1)
        cursor.execute(sql2)
    cursor.commit()
    return redirect('/admin/user-control/')

@app.route('/admin/user-control/free-act/',methods=['POST'])
def free_act():
    if session.get('admin_id')==None or session['Atype'] not in ['超级管理','用户管理']:
        return redirect('/admin/')
    Uno = request.form['id']
    Ano = session['admin_id']
    date = request.form['date']
    cursor = get_cursor()
    sql1 = f"UPDATE UserList SET Urestrict=0 WHERE Uno='{Uno}'"
    sql2 = f"INSERT INTO UAlter VALUES ('{Uno}','{Ano}','{date}','解封','对于用户进行解封')"
    print('涉及语句：',sql1,sql2)
    cursor.execute(sql1)
    cursor.execute(sql2)
    cursor.commit()
    return redirect('/admin/temp/')

@app.route('/admin/admin-control/',methods = ['GET'])
def admin_control():
    if session['Atype']!='超级管理':
        return  redirect('/admin/')
    if request.args.get('p')!=None:
        page = int(request.args.get('p'))
    else:
        page = 1
    cursor = get_cursor()
    U = cursor.execute(f"SELECT * FROM UAlter ORDER BY actDate ASC").fetchall()
    B = cursor.execute(f"SELECT * FROM BAlter ORDER BY actDate ASC").fetchall()
    U = list(U)[(page-1)*5:page*5]
    B = list(B)[(page-1)*5:page*5]
    return render_template('admin_control.html',UAlter=U,BAlter=B,page=page)

# user部分

@app.route('/user/',methods = ['POST', 'GET'])
def user():
    login = False
    error = request.args.get("error")
    if session.get('user_id'):
        login = True
    return render_template('user.html',login=login,error=error,Uname=session.get('Uname'),Utype=session.get('Utype'),Urestrict=session.get('Urestrict'))

@app.route('/user/change-password/',methods = ['GET','POST'])
def user_changepassword():
    Uno = session['user_id']
    if request.method=='GET':
        return render_template('user_changepw.html',error=False)
    else:
        old = get_md5(request.form['old'])
        new = get_md5(request.form['new'])
        date = request.form['date']
        cursor = get_cursor()
        if cursor.execute(f"SELECT * FROM UseList WHERE Uno={Uno} AND Upassword='{old}'").fetchone():
            sql1 = f"UPDATE UserList SET Upassword='{new}' WHERE Uno='{Uno}'"
            sql2 = f"INSERT INTO UAlter VALUES ('{Uno}','Admin002','{date}','修改密码','在{date}对于密码进行了修改')"
            cursor.execute(sql1)
            cursor.execute(sql2)
            cursor.commit()
            return redirect('/user/')
        else:
            return render_template('user_changepw.html',error=True)

@app.route('/user/login/',methods = ['POST'])
def user_login():
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
        session['borrowlist']=[]
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


@app.route('/user/search/',methods = ['GET'])
def book_search():
    # 这个搜索不需要登录要求
    search = None
    page = 1
    if request.args.get('Bname')!=None:
        cursor = get_cursor()
        search = cursor.execute(f"SELECT * FROM book WHERE removed=0 AND Bname LIKE '%{request.args.get('Bname')}%'")
        page = int(request.args.get('p'))
        #print(search)
        search = list(search)[(page-1)*5:page*5]
    return render_template('book_search.html',search=search,page=page,keyword=request.args.get('Bname'))

@app.route('/user/borrow/add/',methods = ['GET'])
def book_add():
    ISBN = request.args.get('ISBN')
    #print('ISBN:',ISBN)
    if session['borrowlist']==None:
        session['borrowlist']=[]
    #print(type(session['borrowlist']),'~',session['borrowlist'])
    temp = session['borrowlist'].copy()
    temp.append(ISBN)
    session['borrowlist'] = temp#这个是session的一个特色，如果是作为对象用append并不能有效修改
    #print('book_add:session[borrowlist]',session['borrowlist'])
    return redirect('/user/borrow/')

@app.route('/user/borrow/',methods = ['POST', 'GET'])
def book_borrow():
    # 借阅需要登录
    if not session.get('user_id') or session['user_id']==None:
        #print(session.get('user_id'))
        return redirect('/user/')

    ISBN = None
    cursor = get_cursor()
    print(session['borrowlist'])
    if session['borrowlist']==None or len(session['borrowlist'])==0:
        target=None
        session['borrowlist']=[]
    else:
        target=[]
        for one in session['borrowlist']:
            print(f"SELECT * FROM book WHERE Bno ={one}")
            cr = cursor.execute(f"SELECT * FROM book WHERE Bno={one}")
            target.append(cr.fetchone())
            print(target)
    #print(session['borrowlist'])
    #print(session.get('user_id'))
    return render_template('book_borrow.html',id=session.get('user_id'),target=target)

@app.route('/user/borrow/act/',methods = ['POST'])
def book_act():
    cursor = get_cursor()
    date = request.form['date']
    Uno = session['user_id']
    for Bno in session['borrowlist']:
        sql1 = f"INSERT INTO Borrow VALUES ('{Uno}','{Bno}','{date}',14,NULL,0,NULL)"
        print(sql1)
        sql2 = f"UPDATE UserList SET Uget =Uget+1 WHERE Uno='{Uno}' "
        sql3 = f"UPDATE Book SET num =num-1 WHERE Bno='{Bno}' "
        cursor.execute(sql1)
        cursor.execute(sql2)
        cursor.execute(sql3)
    cursor.commit()
    session['borrowlist'] = []
    return redirect('/user/')

@app.route('/user/return/')
def book_return():
    # 还书与延期的管理界面
    # 需要登录
    if not session.get('user_id') or session['user_id']==None:
        #print(session.get('user_id'))
        return redirect('/user/')

    cursor = get_cursor()
    sql = f"SELECT Book.Bno,Bname,maxtime FROM Borrow,Book WHERE Uno='{session['user_id']}' AND Book.Bno=Borrow.Bno AND isReturn=0"
    borrowed = cursor.execute(sql)
    return render_template('book_return.html',borrowed=borrowed)

@app.route('/user/return/act/',methods=['POST'])
def book_return_act():
    Uno = session['user_id']
    Bno = request.form['ISBN']
    date = request.form['date']
    cursor = get_cursor()
    sql1 = f"UPDATE UserList SET Uget=Uget-1 WHERE Uno='{Uno}'"
    sql2 = f"UPDATE Borrow SET isReturn=1,returnDate='{date}'  WHERE Uno='{Uno}' AND Bno='{Bno}'"
    sql3 = f"UPDATE Book SET num=num+1 WHERE Bno='{Bno}'"
    print(sql1,sql2,sql3)
    cursor.execute(sql1)
    cursor.execute(sql2)
    cursor.execute(sql3)
    cursor.commit()
    return redirect('/user/return/')

@app.route('/user/return/add-time/',methods=['POST'])
def book_return_addtime():
    Uno = session['user_id']
    Bno = request.form['ISBN']
    cursor = get_cursor()
    sql = f"UPDATE Borrow SET maxtime=21 WHERE Uno='{Uno}' AND Bno='{Bno}'"
    print(sql)
    cursor.execute(sql)
    cursor.commit()
    return redirect('/user/return/')

@app.route('/test/',methods = ['POST', 'GET'])
def test():
    test = [2,3,3]
    return render_template('test.html',test=test)

if __name__ == '__main__':
    app.run(debug=True)
