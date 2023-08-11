# importing dependencies
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import os, re
from flask_socketio import join_room, leave_room, send, SocketIO

from database import log, register
from chat_themes import themes
from account_standard import valid_username, valid_key, confirm_key

# flask standard
app = Flask(__name__, static_folder="static")
app.secret_key = os.urandom(6)

# sockets inclusion
socketio = SocketIO(app)


# opening panel
@app.route("/")
def index():
    return render_template("index.html")

# log in endpoint
@app.route("/login")
def login():
    return render_template("logIn.html")

# sign up enpoint
@app.route("/signup")
def signup():
    return render_template("signUp.html")

# ---------------------------------------------------------------------

# logging in presidure
@app.route("/logging", methods=["POST"])
def logging():
    session.clear()
    session["logged_in"] = False

    # getting the logging form data
    username = request.form["username"]
    password = request.form["pass"]

    # Accesses to the "database.py" file to assess the verification of the logging
    result = log(username, password)

    # feedback or allowance
    if result is None:
        error = "Invalid username or password"
        return render_template("logIn.html", error=error)
    else:
        session["username"] = username
        session["logged_in"] = True
        return redirect(url_for("find_chat"))

# ---------------------------------------------------------------------

# signing up presidure
@app.route("/signing", methods=["POST"])
def signing():

    # getting the logging form data
    username = request.form["username"]
    password = request.form["password"]
    password_confirm = request.form["password_confirm"]

    # Accesses the "account_standard.py" file to verify or reject the comparison of the two passwords
    if confirm_key(password, password_confirm)[0]:
        error = confirm_key(password, password_confirm)[1]
        return render_template("signUp.html", error=error)

    # Accesses the "account_standard.py" file to verify or reject validity of the username
    elif valid_username(username)[0]:
        error = valid_username(username)[1]
        return render_template("signUp.html", error=error)

    # Accesses the "account_standard.py" file to verify or reject validity of the password
    elif valid_key(password)[0]:
        error = valid_key(password)[1]
        return render_template("signUp.html", error=error)

    # Accesses the "database.py" file to verify or reject the availability of the username
    result = register(username, password)
    if result == "Unvailable_username":
        error = "Username already exists"
        return render_template("signUp.html", error=error)
    else:
        session["username"] = username
        session["logged_in"] = True
        return redirect(url_for("find_chat"))

# ------------------------------------------------------------------------

# finding chat endpoint
@app.route("/find_chat", methods=["GET"])
def find_chat():
    if "logged_in" not in session:
        return redirect(url_for("login"))
    username = session.get("username")
    usernames = []

    # Accesses the "chat_themes.py" file to get the available themes
    for i in themes.values():
        usernames.append(i)
    return render_template("findComv.html", usernames=usernames, username=username)

# ----------------------------------------------------------------------------

chats = {}
# chatting endpoint
@app.route("/chatting", methods=["GET"])
def chatting():
    if "logged_in" not in session:
        return redirect(url_for("login"))

    # Getting the username and the Themantic chat room information
    username = session.get("username")
    theme_info = request.args.get("reciever")
    theme_info = theme_info.split()
    theme_id = theme_info[0]
    theme_name = theme_info[1]

    # Registering the themantic chatroom id to the"chat" variable
    # Refgistering the themantic chatroom id to the current chating session
    chat = theme_id
    session["chat"] = chat
    # Declairing 0 members and an empty list of messages to the current chatting session
    chats[chat] = {"members": 0, "messages": []}
    return render_template(
        "chatting.html", theme_name=theme_name, username=username
    )

# --------------------------------------------------------------------

# logging out presidure
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

# ----------------------------------------------------------------------

# getting the themes API
@app.route("/get_themes")
def get_themes():
    return jsonify(themes)

# ----------------------------------------------------------------------

# socket connetion
@socketio.on("connect")
def connect(auth):
    # geting the appropriate data
    chat = session.get("chat")
    username = session.get("username")

    # attempting to enter the chatroom
    if not chat or not username:
        return
    if chat not in chats:
        leave_room(chat)
        return
    # entering the chatroom,
    # sending a message to all current members, announcing the entrance of a new member,
    # incrementing the current member sum
    join_room(chat)
    send({"username": username, "message": f"{username} has entered the chat"}, to=chat)
    chats[chat]["members"] += 1

# socket disconnect
@socketio.on("disconnect")
def disconnect():
    # geting the appropriate data
    chat = session.get("chat")
    username = session.get("username")
    # leaving the chatroom
    leave_room(chat)

    # the user is removed as a member
    # if no other member participate, the session is deleted
    if chat is not None:
        chats[chat]["members"] -= 1
        if chats[chat]["members"] <= 0:
            del chats[chat]
    # a message is send to all other current members, that the user has left the chatroom
    send({"username": username, "message": f"{username} has left the chat"}, to=chat)
    print(f"{username} has left the room {chat}")

# socket messaging presidure
@socketio.on("message")
def message(data):
    # geting the appropriate data
    chat = session.get("chat")


    if chat not in chats:
        return
    # the user's username his text message is send to chatroom with the assistance of Javascript
    # and them appended to the session's messages lists
    # file "chatting.html" in the templates folder
    content = {"username": session.get("username"), "message": data["data"]}
    send(content, to=chat)
    chats[chat]["messages"].append(content)

# Flask conclusion
if __name__ == "__main__":
    host = '127.0.0.1'
    port = 5000
    socketio.run(app, host=host, port=port, debug=True, allow_unsafe_werkzeug=True)
