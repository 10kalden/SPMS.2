from flask import Flask, render_template, request, redirect, url_for, g,session,flash
import sqlite3
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)
app.config['DATABASE'] = 'User_Data.db'
app.config['SECRET_KEY'] = 'secretkey'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/<custom_route>')
def custom_fun(custom_route):
    return f'This page is for {custom_route}'

# user sign-up
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signUp.html')
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()
        if result:
            email = result[0]
            return render_template('signup.html', msg="Email already exists")
        else:
            if password == cpassword:
                hashed_password = generate_password_hash(password)
                cursor.execute('INSERT INTO users (email, name, password, confirmpassword) VALUES (?, ?, ?, ?)', (email, name, hashed_password, cpassword))
                db.commit()

                return render_template('signup.html', msg="Signup successful")
            else:
                return render_template('signup.html', msg='Sign up unsuccessful! Passwords do not match.')

# user log-in
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']
        
        if email=='admin@gmail.com':
            if password == 'admin':
                return redirect('/admin')
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT email, password FROM users WHERE email = ?', (email,))
        result = cursor.fetchone()

        if result:
            stored_email, stored_hashed_password = result
            if check_password_hash(stored_hashed_password, password):
                session['logged_in'] = True
                session['email'] = email;
                return redirect('/user')
            else:
                return render_template('login.html',msg='Incorrect password Please try again error')
        else:
            return render_template('login.html',msg='Email not found. Please sign up error')

        return render_template('login.html')
    
    

@app.route('/')
def form_page():
    return render_template('index.html')

# user page
@app.route('/user',methods=['POST','GET'])
def userpage():
    user_email = session.get('email')

    if user_email:
        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT * FROM TaskList WHERE email = ?', (user_email,))
        data = cursor.fetchall()

        cursor.close()
        db.close()
        return render_template('userpage.html', user_email=user_email, data=data)
    else:
        return render_template('userpage.html',msg="no task for you at the moment .... ")  

# admin page
@app.route('/admin', methods=['POST', 'GET'])
def adminpage():
    if request.method == 'GET':
        return redirect('/get_all_data')
    elif not session.get('logged_in'):
        flash('You must log in to access this page.', 'error')
        return redirect(url_for('login'))
    else:
        email = request.form['email']
        task = request.form['task']
        status = 0

        db = get_db() 
        cursor = db.cursor()
                
        create_table_sql = '''
            CREATE TABLE IF NOT EXISTS TaskList (
                taskid INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                task TEXT,
                task_completed BOOLEAN
            )
        '''
        cursor.execute(create_table_sql)
        db.commit()

        cursor.execute('INSERT INTO TaskList (email, task,task_completed) VALUES (?,?, ?)', (email, task,status))
        db.commit()
        
        return redirect('/get_all_data');

# Create project
@app.route('/get_all_data')
def get_all_data():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT * FROM TaskList')

    data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('adminpage.html', data=data)

@app.route('/mark_task_completed/<int:taskid>', methods=['POST'])
def mark_task_completed(taskid):
    
    db = get_db()
    cursor = db.cursor()

   
    cursor.execute('UPDATE TaskList SET task_completed = 1 WHERE taskid = ?', (taskid,))
    db.commit()

    return redirect('/user')

# log-out
@app.route('/logout')
def logout():
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)







