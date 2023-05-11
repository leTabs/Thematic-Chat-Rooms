from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3, hashlib, os
from datetime import timedelta
from flask_socketio import join_room, leave_room, send, SocketIO, emit

app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(16)
socketio = SocketIO(app)

chats = {}
usernames = []
conn = sqlite3.connect('profiles.db')
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")
conn.commit()
conn.close()


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/login')
def login():
    return render_template('logIn.html')
@app.route('/signup')
def signup():
    return render_template('signUp.html')
#========================================================================
@app.route('/login_step', methods=['POST'])
def process_login():
    session.clear()
    # get the login form data
    username = request.form['username']
    password = request.form['pass']
    #stay_logged = request.form.get('stayLogged')
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        error = 'Invalid username or password'
        return render_template('logIn.html', error = error)
    else:
        hashed_password = result[0]
        hashed_input_password = hashlib.sha256(password.encode()).hexdigest()
        if hashed_input_password != hashed_password:
            conn.close()
            error = 'Invalid username or password'
            return render_template('logIn.html', error = error)
        else:
            conn.close()
            session['username'] = username
            session['logged_in'] = True
            #session.modified =True
            return redirect(url_for('success'))
#------------------------------------------------------------------
@app.route('/register', methods=['POST'])
def process_signup():
    username = request.form['username']
    password = request.form['password']
    password_confirm = request.form['password_confirm']
    #stay_logged = request.form.get('stayLogged')
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone() is not None:
        conn.close()
        error = 'Username already exists'
        return render_template('signUp.html', error = error)
    elif password != password_confirm:
        error = 'The passwords don\'t match'
        return render_template('signUp.html', error = error)
    else:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        #maybe i don't need that actually
        conn.close()
        return redirect(url_for('success'))

@app.route(f'/find', methods=['GET'] )
def success():
    #session
    username = session.get('username')
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users')
    all_usernames = [row[0] for row in cursor.fetchall()]
    if username == session.get('username'):
           if username not in usernames:
               usernames.append(username)
    conn.close()
    user = session.get('username')
    user_id = str(usernames.index(user) + 1)
    session['own'] = user_id
    print('*'*60)
    return render_template('findSomeone.html', usernames=usernames, user=user )

@app.route(f'/find/chat', methods=['GET'] )
def chat():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    print('-'*40)
    user = session.get('username')
    print('[USER]:  ', user)
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users')
    all_usernames = [row[0] for row in cursor.fetchall()]
    for i in all_usernames:
        if i == session.get('username'):
           if i not in usernames:
               usernames.append(i)
        print(i)
    user_id = str(usernames.index(user) + 1)
    print('[USER_ID]:', user_id )
    info = request.args.get('rec')
    info = info.split()
    rec_id = info[0]
    rec = info[1]
    print('[RECIVER]:', rec)
    print('[RECIVER ID]: ', rec_id)
    print('-'*40)
#    session['user_field']= user_id
    chat = ''
    if rec_id not in chats:
        print(rec_id , 'NOT IN SESSION')
        chat = user_id
        session['chat'] = chat
        chats[chat] = {"members": 0,  "messages":[]}
        print(chats)
        print(session.get('chat'))
        print('[CURRENT SESION]: ', session.get('chat'))
    elif rec_id in chats:
        session['chat'] = rec_id
        print('[CURRENT SESION]: ', session.get('chat'))
    conn.close()
    return render_template('chatting.html', rec=rec, user=user)

@socketio.on("message")
def message(data):
    chat = session.get('chat')
    if chat not in chats: return
    content = {'username': session.get('username'), "message": data['data']}
    send(content, to=chat)
    chats[chat]['messages'].append(content)
    print(f"{session.get('username')} said: {data['data']}")


@socketio.on('connect')
def connect(auth):
    chat = session.get('chat')
    username = session.get('username')
    if not chat or not username: return
    if chat not in chats:
        leave_room(chat)
        return
    join_room(chat)
    send({'username': username, 'message': 'has entered the chat'}, to=chat)
    chats[chat]['members'] += 1
    print(f"{username} joined chat {chat}")
    print(chats[chat]['members'])

@socketio.on('disconnect')
def disconnect():
    chat = session.get('chat')
    username = session.get('username' )
    leave_room(chat)
    if chat is not None:
        chats[chat]["members"] -= 1
        if chats[chat]["members"] <= 0:
            del chats[chat]
    send({'username': username, 'message':"has left the chat"}, to=chat)
    print(f"{username} has left the room {chat}")

if __name__ == '__main__':
#    app.run()
    socketio.run(app, debug=True,allow_unsafe_werkzeug= True)
   # app.close()
