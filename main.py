from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import os
#from datetime import timedelta
from flask_socketio import join_room, leave_room, send, SocketIO
from database import log, register, find_and_chat
from chat_themes import themes
import sqlite3,json

 
app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(6)
#app.config['PERMANENT_SESSION_LIFE'] = timedelta(2)
socketio = SocketIO(app)

# utilities
chats = {}
#usernames = [] 


# flask up routers
@app.route('/')
def index():
    #session.clear()
    return render_template('index.html')
@app.route('/login')
def login():
    return render_template('logIn.html')
@app.route('/signup')
def signup():
    return render_template('signUp.html')

#---------------------------------------------------------------------
@app.route('/logging', methods=['POST'])
def logging():
    session.clear()
    session['logged_in'] = False
    username = request.form['username']
    password = request.form['pass']
    result = log(username, password)
    if result is None:
        error = 'Invalid username or password'
        return render_template('logIn.html', error = error)
    elif result == 'Unmatched':
        error = 'Invalid username or password'
        return render_template('logIn.html', error = error)
    else: 
        session['username'] = username
        session['logged_in'] = True
        return redirect(url_for('find_chat'))
#---------------------------------------------------------------------
@app.route('/signing', methods=['POST'])
def signing():
    username = request.form['username']
    password = request.form['password']
    password_confirm = request.form['password_confirm']
    if password != password_confirm:
        error = 'The passwords don\'t match'
        return render_template('signUp.html', error=error)
    result = register(username, password)

    if result == 'Unvailable_username': 
        error = 'Username already exists'
        return render_template('signUp.html', error = error)
    else: 
        return redirect(url_for('find_chat'))
#------------------------------------------------------------------------
@app.route('/find_chat', methods=['GET'])
def find_chat(): 
    if 'logged_in' not in session:
        return redirect(url_for('login')) 
    username = session.get('username')
    #usernames = find_and_chat(username) #ook at it later
    usernames = []
    for i in themes.values():
        usernames.append(i) 
    return render_template('findComv.html', usernames=usernames, username=username )
#----------------------------------------------------------------------------
@app.route('/chatting', methods=['GET']) 
def chatting():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    username = session.get('username')
    usernames = find_and_chat(username)
    user_id = str(usernames.index(username) + 1)

    receiver_info = request.args.get('reciever')
    receiver_info = receiver_info.split()
    receiver_id = receiver_info[0]
    receiver_name = receiver_info[1]
    chat = receiver_id
    session['chat'] = chat
    chats[chat] = {"members": 0,  "messages":[]}
    return render_template('chatting.html', receiver_name=receiver_name, username=username)
#---------------------------------------------------------------------
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))
#----------------------------------------------------------------------
@app.route('/get_themes')
def get_themes(): return jsonify(themes)

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

if '__main__' == __name__:
    if __name__ == '__main__':
        socketio.run(app, debug=True,allow_unsafe_werkzeug= True)
