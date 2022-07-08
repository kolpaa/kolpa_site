from crypt import methods
from distutils.log import debug
from flask import Flask, render_template, url_for, request, session, redirect, g, flash
import os, sqlite3, re
from FDataBase import FDataBase
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = "kolpa.db"
DEBUG = True
SECRET_KEY = 'sfdggrege21dsvdfvdvdad3'
PASSWORD = '123'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.static_folder,'kolpa.db')))

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.route("/")
def home():
    return render_template('index.html')

@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/shawarma_rating", methods=["POST", "GET"])
def shawarma():
    if request.method == "POST" and session['admin']:
        if request.form['place'] != "" and request.form['link'] != "" and request.form['name'] != "" and request.form['mark'] != "" and request.form['rating'] != "":
            dbase.addShawarma(request.form['name'], request.form['place'], request.form['mark'], request.form['rating'], request.form['link'])
            flash('Added', category='success')
        else:
            flash('Error', category='error')
        return redirect(url_for('shawarma'))
    return render_template('shawarma_rating.html', shaws = dbase.getShawsData(), admin = session['admin'])  


@app.route("/cat", methods=["POST", "GET"])
def cat():
    if request.method == 'POST' and session['admin']:
        print(request.files)
        if 'photo' not in request.files:
            flash('Cant read a file', category='error')
            return redirect(request.url)
        file = request.files['photo']
        if file.filename == '':
            flash('There is no file', category='error')
            return redirect(request.url)
        if file:         
            time = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
            file.save(os.path.join("static/files/kusya", str(time) + '.png'))
            dbase.addCatPhoto(request.form['description'], 'static/files/kusya/' + str(time) + '.png')
            flash('Added', category='success')
        return redirect(url_for('cat'))
    return render_template('kusya.html', cat = dbase.getCatData(), admin = session['admin'])  

@app.route("/blog/<url>", methods=["POST", "GET"])
def showPost(url):
    dbase.addVisit(url)
    if request.method == "POST":
        if request.form['comment'] != '':           
            dbase.addComment(request.form['comment'], int(session['admin']), 0, url)
        return redirect("/blog/" + url)
    title, post, date, visits = dbase.getPost(url)
    comments = dbase.getComments(url)
    return render_template('post.html',  visits = visits, date = date, comments = comments, title=title, post=post, admin = session['admin'], url=url)

@app.route("/blog", methods=["POST", "GET"])
def blog():
    search = ''
    sort = 'Новые'
    if request.method  == 'POST' and session['admin'] and request.form.get('post') != None:
        if request.form['title'] != "" and request.form['content'] != "" and request.form['url'] != "":
            if os.path.isdir('static/files/posts_res/' + request.form['url']) :
                flash('Error', category='error')
            else:
                os.mkdir('static/files/posts_res/' + request.form['url'])
                files = request.files.getlist('images')
                for file in files:
                    if file.filename != '':
                        file.save(os.path.join("static/files/posts_res/" + request.form['url'], file.filename))
                base = "../static/files/posts_res/" + request.form['url']
                content = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>"+base+"/\\g<url>>",
                          request.form['content'])
                dbase.addPost(request.form['title'], request.form['url'], content)
                flash('Added', category='success')
        return redirect(url_for('blog'))
    elif request.method  == 'POST' and request.form.get("search") != None:
        sort = request.form["Sort method"]
        search = request.form["text"]
    return render_template('blog.html', posts=dbase.getBlogData(search, sort), admin = session['admin'])  

@app.route("/resume")
def resume():
    return render_template('resume.html') 

@app.route("/books", methods=["POST", "GET"])
def books():
    if request.method == 'POST' and session['admin']:
        print(request.files)
        if 'book' not in request.files:
            flash('Cant read a file', category='error')
            return redirect(request.url)
        file = request.files['book']
        if file.filename == '':
            flash('There is no file', category='error')
            return redirect(request.url)
        if file:   
            if request.form['title'] != "":
                file.save(os.path.join("static/files/books", request.form['title']))
                dbase.addBook(request.form['author'], request.form['title'], 'static/files/books/' + request.form['title'])
                flash('Added', category='success')
            else:
                flash('No title', category='error')
        return redirect(url_for('books'))
    return render_template('books.html', books = dbase.getBooksData(), admin = session['admin'])


@app.route("/admin", methods=["POST", "GET"])
def admin():
    if request.method == "POST":
        if request.form.get('password') != None:    
            hash = generate_password_hash(request.form['password'])   
            if check_password_hash(hash, dbase.getPassword()):
                session['admin'] = True
        elif session['admin']:
            session['admin'] = False
        return redirect(url_for('admin'))
    return render_template('admin.html',  admin = session['admin'])  


@app.route("/mysites/<int:id>", methods=["POST", "GET"])
def delete_site(id):
    if request.method == "POST" and session['admin']:
            dbase.deleteSite(id)
    return redirect(url_for('mysites'))

@app.route("/shawarma/<int:id>", methods=["POST", "GET"])
def delete_shawarma(id):
    if request.method == "POST" and session['admin']:
            dbase.deleteShawarma(id)
    return redirect(url_for('shawarma'))

@app.route("/cat/<int:id>", methods=["POST", "GET"])
def delete_catPhoto(id):
    if request.method == "POST" and session['admin']:
            dbase.deleteCatPhoto(id)
    return redirect(url_for('cat'))


@app.route("/blog/<int:id>", methods=["POST", "GET"])
def delete_post(id):
    if request.method == "POST" and session['admin']:
            dbase.deletePost(id)
    return redirect(url_for('blog'))

@app.route("/blog/comment/<int:id>", methods=["POST", "GET"])
def action_comment(id):
    url = dbase.getURL(id)

    if request.method == "POST" and session['admin'] and request.form.get('delete') != None:
            dbase.deleteComment(id)
    elif request.form['reply'] != '' and session['admin']:
            dbase.addComment(request.form['reply'], 1, id, url)
    return redirect('/blog/' + url)

@app.route("/books/<int:id>", methods=["POST", "GET"])
def delete_book(id):
    if request.method == "POST" and session['admin']:
            dbase.deleteBook(id)
    return redirect(url_for('books'))


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('404.html'), 404

@app.before_request
def before_request():
   global dbase
   db = get_db()
   dbase = FDataBase(db)
   if 'admin' not in session:
       session['admin'] = False

if __name__ == "__main__":
    app.run(host='0.0.0.0')
