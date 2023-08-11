# importing dependencies
import sqlite3, os , hashlib

# connect to the user's database (it is created if it does not exist)
# a "users" tables is created if it does not exist to host the usernames and passwords
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
# the database connection is terminated



# if the username exists, users password is decripted and checks if it matches the given one during the logging

# logging in
def log(nick, key):
    # connects to the database
    connection = sqlite3.connect('usersDtabase.db')
    cursor = connection.cursor()
    # attempts to get the password that corresponds to the giver username
    cursor.execute("SELECT password FROM users WHERE username = ?", (nick,))
    value = cursor.fetchone()
    # returns "Access allowed" if the username and corresponding decrypted password are correct
    # returns None if the username doesn't exist or the corresponding password is incorrect
    if value is None:
        return None
    else:
        hashed_password = value[0]
        hashed_input_password = hashlib.sha256(key.encode()).hexdigest()
        if hashed_input_password != hashed_password:
            return None
        else:
            return "Access allowed"

# signing up
def register(nick, key):
    # connects to the database
    connection = sqlite3.connect('usersDtabase.db')
    cursor = connection.cursor()
    # attempts to get existing information for the giver username
    cursor.execute("SELECT * FROM users WHERE username = ?", (nick,))
    # if information exists, the username is not available
    # if no information exists, the username and it's encrypted password is stored in the database
    if cursor.fetchone() is not None:
        return 'Unvailable_username'
    else:
        hashed_password = hashlib.sha256(key.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (nick, hashed_password))
        connection.commit()
        connection.close()
        return
