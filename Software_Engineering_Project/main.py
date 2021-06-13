from flask import Flask, redirect, flash, session, escape, url_for, render_template, request, abort, make_response
import sqlite3
import os
from werkzeug.utils import secure_filename
import datetime as dt
import sqlite3

app = Flask(__name__)

app.secret_key = 'software_engineering'


def signin_db(userid, userpw):
    conn = sqlite3.connect("userinfo.db", isolation_level=None)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS test \
                   (id text PRIMARY KEY, password text)")
    conn.commit()
    c.execute("SELECT * FROM test")
    rows = c.fetchall()
    conn.close()
    for row in rows:
        if row[0] == userid:
            if row[1] == userpw:
                return 'success'
            else:
                return 'fail'

    return 'fail'

def signup_db(userid, userpw):
    conn = sqlite3.connect("userinfo.db", isolation_level=None)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS test \
           (id text PRIMARY KEY, password text)")
    conn.commit()

    c.execute("SELECT * from test WHERE id = '%s'" % userid)
    id_row = c.fetchall()

    if len(id_row) != 0:
        conn.close()
        return 'exist'

    else:
        c.execute("INSERT INTO test (id, password) VALUES(?,?)",
                (userid, userpw))
        conn.commit()
        conn.close()
        return 'ok'
    conn.commit()
    conn.close()
    return 'done'

def diarydb(userid, title, content, photo):
    conn = sqlite3.connect("diaryinfo.db", isolation_level=None)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS diary \
               (id text, date datetime, title text, content text, photo text)")

    date = dt.datetime.now()
    c.execute("INSERT INTO diary (id, date, title, content, photo) VALUES(?,?,?,?,?)",
              (userid, date, title, content, photo))
    conn.commit()
    conn.close()

def updatediary(origin, userid, title, content, photo):
    conn = sqlite3.connect("diaryinfo.db", isolation_level=None)
    c = conn.cursor()
    date = dt.datetime.now()
    c.execute("DELETE FROM diary WHERE date = '%s'" % origin)
    conn.commit()
    c.execute("INSERT INTO diary (id, date, title, content, photo) VALUES(?,?,?,?,?)",
              (userid, date, title, content, photo))

    conn.commit()
    conn.close()


def deletediary(time):
    conn = sqlite3.connect("diaryinfo.db", isolation_level=None)
    c = conn.cursor()
    c.execute("DELETE FROM diary WHERE date = '%s'" % time)
    conn.commit()
    conn.close()

def readdiary(userid):
    conn = sqlite3.connect("diaryinfo.db", isolation_level=None)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS diary \
                   (id text, date datetime, title text, content text, photo text)")
    conn.commit()
    #c.execute("SELECT * from diary ORDER BY date DESC")
    c.execute("SELECT * from diary WHERE id = '%s'" % userid)
    rows = c.fetchall()
    rows.reverse()
    conn.commit()
    conn.close()
    return rows

def finddiary(date):
    conn = sqlite3.connect("diaryinfo.db", isolation_level=None)
    c = conn.cursor()
    c.execute("SELECT * from diary WHERE date = '%s'" % date)
    rows = c.fetchall()
    rows.reverse()
    conn.commit()
    conn.close()
    return rows


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        if signin_db(request.form['profName'], request.form['password']) == 'fail':
            flash('아이디 혹은 비밀번호가 잘못 입력되었습니다.')
            return redirect(url_for('index'))
        elif signin_db(request.form['profName'], request.form['password']) == 'success':
            session['username'] = request.form['profName']
            flash(request.form['profName']+'님, 환영합니다!')
            return redirect(url_for('mypage'))
        else:
            flash('아이디 혹은 비밀번호가 잘못 입력되었습니다.')
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/mypage')
def mypage():
    user_id = session.get('username')
    if request.method == 'POST':
        try:
            date = request.form['id']
        except:
            pass
        else:
            return redirect(url_for('update', id = date))
    return render_template('mypage.html', result = readdiary(user_id))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('로그아웃 되었습니다.')
    return redirect(url_for('index'))

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        id = request.form['profName']
        pw = request.form['password']
        if id == '':
            flash("아이디를 입력해주세요.")
            return redirect(url_for('signup'))
        elif pw == '':
            flash("비밀번호를 입력해주세요.")
            return redirect(url_for('signup'))
            return redirect(url_for('signup'))
        if signup_db(id, pw) == 'exist':
            # 이미 존재하는 아이디
            flash("이미 존재하는 아이디입니다.")
            return redirect(url_for('signup'))
        else:
            # 회원가입 성공
            flash("회원가입이 완료되었습니다!")
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/addDiary', methods = ['GET', 'POST'])
def addDiary():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if title == '':
            flash('제목을 입력해주세요.')
            return render_template('addDiary.html')
        elif content == '':
            flash('내용을 입력해주세요.')
            return render_template('addDiary.html')

        try:
            f = request.files['file']
        except:
            diarydb(session['username'], title, content, '')
        else:
            if not os.path.exists("./static"):
                os.makedirs("./static")
            f.save("./static/" + secure_filename(f.filename))

            diarydb(session['username'], title, content, secure_filename(f.filename))

        flash("일기가 저장되었습니다.")
        return redirect(url_for('mypage'))
    return render_template('addDiary.html')

@app.route('/update/<string:id>', methods=['POST', 'GET'])
def update(id):
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        try:
            f = request.files['file']
        except:
            updatediary(id, session['username'], title, content, '')
        else:
            if not os.path.exists("./static"):
                os.makedirs("./static")
            f.save("./static/" + secure_filename(f.filename))
            updatediary(id, session['username'], title, content, secure_filename(f.filename))

        flash("일기가 수정되었습니다.")
        return redirect(url_for('mypage'))
    diary = finddiary(id)
    return render_template('update.html', diary = diary[0])

@app.route('/tmp/<string:id>', methods = ['POST', 'GET'])
def tmp(id):
    deletediary(id)
    return redirect(url_for('mypage'))

if __name__ == '__main__':
    app.run(debug = True)