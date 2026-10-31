# Main connection import
import socket
# Allows concurrent processing 
import threading
# Converts binary to dictionary datatypes
from protocol import encode,decode

# Defines the client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Variable indicated whether a match is in session
gameStart = False

serverData = False

connectedPlayers = {}

playerID = None

questionsids = []

submittedPlayers = []

round = False

questionsCorrect = {}

playerLeft = False

serverFull = False

hasStarted = False

# Connects to the server
def connect(name,equippedItem): 
    host = "127.0.0.1"
    port = 9999

    try:
        # host and port to be used
        client.connect((host,port)) 

        client.send(encode("JOIN GAME",{
            "name": name,
            "equippedItem": equippedItem
        }))

        # Constantly listens for a server
        threading.Thread(target=listenToServer, daemon= True).start() 

    except Exception:
        return False

    return True

# Listens to the server continually
def listenToServer(running = True):

    global playerLeft

    while running:
        try:
            # Client recieves data in 4096 bytes format
            data = client.recv(4096) 

            if not data and playerLeft == False:
                playerLeft = True
                client.close()
                break
            # Decodes the message sent by the server
            serverMessage = decode(data)

            # Handles the message
            handleMessage(serverMessage)

        except Exception:
            playerLeft = True
            client.close()
            break

# Checks the state of the server
def checkServer():
    global playerLeft,hasStarted,serverFull

    if playerLeft:
        endConnectionClient()
        return(True,"left")
    
    elif serverFull:
        return(True,"full")

    elif hasStarted:
        return(True,"start")
    
    else:
        return(False,"")

# Handles the message type 
def handleMessage(serverMessage):
    global questionsids
    global round

    data = serverMessage["data"]


    if serverMessage["type"] == "QUESTION IDS":
        global questionsids

        # Gives an array of quesiton ids {need to search through them and fetch the question}
        questionsids = data["questionids"]
    
    # Checks if game is ready
    elif serverMessage["type"] == "PLAYERS CONNECTED":
        global connectedPlayers
        
        connectedPlayers = data["players"]
        global gameStart

        round = True
        gameStart = True

    elif serverMessage["type"] == "PLAYER ID":
        global playerID
        playerID = data

    elif serverMessage["type"] == "SERVER STATS":
        
        connectedPlayers = data

        global serverData

        serverData = True
    
    elif serverMessage["type"] == "SUBMITTED PLAYERS":
        global submittedPlayers
        submittedPlayers = data
    
    elif serverMessage["type"] == "ROUND END":
        round = False

    elif serverMessage["type"] == "QUESTIONS CORRECT":
        global questionsCorrect

        questionsCorrect = data

    elif serverMessage["type"] == "SERVER END":
        global playerLeft

        playerLeft == True

    elif serverMessage["type"] == "FULL":
        global serverFull

        serverFull = True

    elif serverMessage["type"] == "IN PROGRESS":
        global hasStarted

        hasStarted = True

# Fetch the questions ids
def fetchQuestionidsFromServer():
    global questionsids

    return questionsids

# Updates the server of the clients stats
def updateStats(isCorrect,timing, points):
    global playerID
    try:
        client.send(encode("PLAYER STATS",{
                "ID": playerID,
                "isCorrect": isCorrect,
                "timing": timing,
                "points": points
                }))

    except Exception as e:
        print("Failed to send stats", e)

# Checks if data is sent
def dataSentCheckerClient():
    global serverData

    if serverData:
        serverData = False
        return True
    else: 
        return False

# Retrieves all the players connected in session
def retrievePlayersClient():
    global connectedPlayers
    global playerID
    
    tempConnectedPlayers = connectedPlayers.copy()

    tempConnectedPlayers.pop(str(playerID))

    return tempConnectedPlayers

# Resets all global Variables for next connection
def endConnectionClient():
    global gameStart,serverData,connectedPlayers,playerID,questionsids,submittedPlayers,round,questionsCorrect,playerLeft,serverFull,hasStarted

    gameStart = False

    serverData = False

    connectedPlayers = {}

    playerID = None

    questionsids = []

    submittedPlayers = []

    round = False

    questionsCorrect = {}

    playerLeft = False

    serverFull = False

    hasStarted = False

    client.close()

# Tells the server that a player has submitted their answer
def tellServerSubmitAnswer():
    global playerID

    client.send(encode("SUBMIT", playerID))

# Checks which players have submitted
def checkSubmittedPlayersClient():
    global submittedPlayers
    
    return submittedPlayers

# Retirevs all of the players score
def retrievePlayerScoreClient():
    global playerID
    global connectedPlayers

    if str(playerID) in connectedPlayers:
        return (connectedPlayers[str(playerID)]["points"])
    else:
        return False

# Resets the array determining which players have submitted
def resetSubmittedPlayersClient():
    global submittedPlayers

    submittedPlayers = []

# Checks if client  is correct
def isPlayerCorrectClient():
    return connectedPlayers[str(playerID)]["isCorrect"]

# Retrieves the clients ID
def retrievePlayerID():
    global playerID

    return playerID

# Checks if round is in progress
def roundInProgress():
    global round

    if round and playerLeft == False:
        return "Continue"
    elif playerLeft == True:
        return "Left"
    else:
        return "End Round"