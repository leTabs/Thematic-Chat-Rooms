import sqlite3, os , hashlib
connection = sqlite3.connect('usersDtabase.db')
cursor = connection.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")
connection.commit()
connection.close()

usernames = []

def log(nick, key):
    connection = sqlite3.connect('usersDtabase.db')
    cursor = connection.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (nick,))
    value = cursor.fetchone()
    if value is None:
        return None
        #password
    else:
        hashed_password = value[0]
        hashed_input_password = hashlib.sha256(key.encode()).hexdigest()
        if hashed_input_password != hashed_password:
            return 'Unmatched'
        else:
            return 'Done'


def register(nick, key):
    connection = sqlite3.connect('usersDtabase.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (nick,))
    if cursor.fetchone() is not None:
        return 'Unvailable_username'
    else:
        hashed_password = hashlib.sha256(key.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (nick, hashed_password))
        connection.commit()
        #maybe i don't need that actually
        connection.close()
        return 'Done'

def find_and_chat(user_name):
    connection = sqlite3.connect('usersDtabase.db')
    cursor = connection.cursor()
    cursor.execute('SELECT username FROM users')
    all_usernames = [row[0] for row in cursor.fetchall()]
    #if username == session.get('username'):
    if user_name not in usernames:
        usernames.append(user_name)
    return usernames

