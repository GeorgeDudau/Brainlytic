import sqlite3 # Accessing Databases
import hashlib # Accessing Salts and Hash
import os 
import secrets # Used to generate one time codes
from email.mime.text import MIMEText # Displays main body of email
# Creates a session token
def createSession(userid,sessions):

    # Random set of 16 unique characters
    token = secrets.token_urlsafe(16)

    # Edits sessions dictionary with the user Id (For searching databases later on)
    sessions[token] = {
        "userid": userid
    }
    return token

# Obtains the user ID from the database
def fetchUserID(emailAddress):

    # Connects to database
    connect = sqlite3.connect("credentials.db")
    cursor = connect.cursor()

    # Fetches only userID 
    cursor.execute("SELECT userid FROM credentials WHERE emailAddress= ?",
                   (emailAddress,))
    result = cursor.fetchone()[0]
    connect.close()
    return(result)

# Fetches the users' name
def fetchUserName(userid):

    # Connects to database
    connect = sqlite3.connect("credentials.db")
    cursor = connect.cursor()

    # Fetches only name of the user
    cursor.execute("SELECT fullName FROM credentials WHERE userid = ?",
                   (userid,))
    result = cursor.fetchone()[0]
    connect.close()
    return result

# Ensures that requested session is active 
def validateSessions(token,sessions):
    if token in sessions:
        return True
    else:
        return False
    
# Removes any sessions in operation
def destroySessions(token,sessions):
    sessions.pop(token,None)

# Gets the user id from the session
def useridFromSession(token, sessions):
    return sessions[token]["userid"]

# Checks to see if provided email and password is valid
def loginProcess(emailAddress,password):

    # Connects to database and queries email, salt and hash
    try:

        connect = sqlite3.connect("credentials.db")
        cursor = connect.cursor()
        cursor.execute("SELECT emailAddress, salt, passwordHash FROM credentials WHERE emailAddress = ?",
                                (emailAddress,))
        
        # Checks for valid emails in database
        try:
            retrievedEmail, salt, passwordHash = cursor.fetchone()
        except TypeError:
            return(False)
        
        # Checks if password matches one in database
        givenPassword = hashPassword(password,bytes.fromhex(salt))
        if givenPassword[1] == passwordHash:
            return True
        else:
            return False
    except:
        return False

# Hashes provided password
def hashPassword(password,salt = None):

    # Generate new salt if none is provided
    if salt is None:
        salt = os.urandom(16)

    # Generates hash using salt
    passwordHash = hashlib.pbkdf2_hmac("sha256",password.encode(), salt, 100_000)

    # Converted into hexadecimal strings for database
    return salt.hex(), passwordHash.hex()

# Checks if email doesnt already exist
def existingEmailCheck(email):
    try:
        # Provides connection to database file
        connect = sqlite3.connect("credentials.db")
        cursor = connect.cursor()
        
        # Checks if a record exists and returns either true or false
        cursor.execute("SELECT 1 FROM credentials WHERE emailAddress = ?",
                       (email,))
        exists = cursor.fetchone()
        connect.close()
        return(exists)
    
    # This error is returned in case the database cannot fetch the data
    except sqlite3.Error:
        return(False)

# Adds the users credential into a database
def signupProcess(fullName,emailAddress,password):

    # Provides connection to database file
    connect = sqlite3.connect("credentials.db")

    # Creates a table for the user if not already created
    cursor = connect.cursor()
    credentialsCreate = "CREATE TABLE IF NOT EXISTS " \
    "credentials(userid INTEGER PRIMARY KEY AUTOINCREMENT,fullName TEXT, emailAddress TEXT , salt TEXT, passwordHash TEXT, points INTEGER DEFAULT 100)"
    cursor.execute(credentialsCreate) 

    #Stores salt and hash
    salt, passwordHash = hashPassword(password)

    # Inserts inputted data if valid
    cursor.execute("INSERT INTO credentials (fullName, emailAddress, salt, passwordHash) VALUES (?,?,?,?)",
                (fullName,emailAddress,salt,passwordHash)
                )
    cursor.execute("SELECT* FROM credentials")

    # Closes database to prevent it from being locked
    results = cursor.fetchall()
    connect.commit()
    connect.close()



