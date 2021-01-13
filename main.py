from flask import Flask, render_template,request, session, redirect, url_for
from flask_mysqldb import MySQL
import json
from flask_mail import Mail
from datetime import datetime

with open('config.json', 'r') as c:
    params=json.load(c)["params"]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'work_hard_bro'



app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME =  params["social_media"]['gmail_name'],
    MAIL_PASSWORD = params["social_media"]['password']
)
mail=Mail(app)

app.config['MYSQL_HOST'] = params["local_server"]['Host']
app.config['MYSQL_USER'] = params["local_server"]['USER']
app.config['MYSQL_PORT'] = params["local_server"]['PORT']
app.config['MYSQL_DB'] = params["local_server"]['DB']

mysql = MySQL(app)

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM post")
    post = cur.fetchall()
    cur.close()
    return render_template('index.html', param=params,post=post)

@app.route('/about')
def about():
    return render_template('about.html',param=params)

@app.route('/post/<string:post_slug>', methods=['GET','POST'])
def post_route(post_slug):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM post WHERE Slug= %s ", [post_slug])
    post=cur.fetchall()
    cur.close()

    return render_template('post.html', param=params, post=post)

@app.route('/login')
def login():
    return render_template('sign.html',param=params )


@app.route('/dashboard', methods=['GET','POST'] )
def dashboard():
    if ('user' in session and session['user'] == params['login']['user']) :
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM post")
        post = cur.fetchall()
        cur.close()
        return render_template('Admin.html', param=params, post=post)
    if request.method == 'POST':
        username= request.form.get('uname')
        userpass = request.form.get('pass')
        if (username == params['login']['user'] and userpass == params['login']['password']) :
            session['user'] = username
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM post")
            post = cur.fetchall()
            cur.close()
            return render_template('Admin.html', param=params,post=post)

    return render_template('sign.html')



@app.route('/edit/<int:sno>', methods=['GET','POST'] )
def edit(sno):
    if ('user' in session and session['user'] == params['login']['user']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            date = datetime.now()

            if sno == '0' :
                cur.execute("INSERT INTO post(Title, Slug, Content, Date) VALUES (%s, %s, %s, %s )",(box_title, slug, content, date))
                mysql.connection.commit()
                cur.close()
            else :
                cur.execute("UPDATE post SET Title= %s, Slug= %s, Content= %s, Date= %s WHERE SNO= %s",(box_title, slug, content, date, sno ))
                mysql.connection.commit()
                cur.close()
                return redirect(url_for('/edit/'+sno))

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM post")
        post = cur.fetchall()
        cur.close()
        return render_template('edit.html',param= params, post=post,sno=sno)


@app.route('/contact', methods=['GET','POST'] )
def contact():
    if request.method == 'POST':

        Name=request.form.get('name')
        Email = request.form.get('email')
        Phone = request.form.get('phone')
        Message = request.form.get('message')

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO enquiry(Name,Email,Phone,Message) VALUES (%s, %s, %s, %s)", (Name,Email,Phone,Message))
        mysql.connection.commit()
        cur.close()

        mail.send_message( 'message form blog',
                           sender=Email,
                           recipients= [params["social_media"]['gmail_name']],
                           body= Message)
        return 'success'

    return render_template('contact.html', param=params)

if __name__=='__main__':
    app.run(debug=True)
