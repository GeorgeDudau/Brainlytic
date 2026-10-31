# Main connection import
import socket 
# Converts binary to dictionary datatypes
from protocol import encode, decode 
# Allows concurrent processing 
import threading 

# Stores the player id of all the clients so this can be fetched
clients = {} 

# Stores the player information of all the players in game
connectedPlayers = {} 

dataSent = 0

submittedPlayers = []

questionsCorrect = {}

playerLeft = False

hasStarted = False

def updateDetails(name,equippedItem):
    global connectedPlayers

    # Adds all information of host
    connectedPlayers[0] = {
        "name": name,
        "points": 0,
        "equippedItem": equippedItem,
        "timing": None,
        "isCorrect": None
    } 



# Starts the server 
def startServer():
    global server
    # Sets the socket type as an internet connection
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Indicates local IP address and port number
    server.bind(("0.0.0.0",9999)) 

    # Indicates the server is looking for connections
    server.listen() 

# Accepts any clients requesting connection
def acceptClients(): 
    while True:

        try:

            # Accepts the client connection 
            client, addr = server.accept() 

            # Concurrently processes the clients message (concurrent otherwise program freezes)
            threading.Thread( 
                target=handleClient,
                args=(client,),
                daemon=True
            ).start()
        except OSError:
            break

# Handles the clients message
def handleClient(client):

    global playerLeft 

    try:
        # Allows server to constantly recieve information from other users infinitely
        while True: 
            # Allows up to 4096 bytes of data from the client to be recieved
            data = client.recv(4096) 
            
            # Client disconnects 
            if not data and playerLeft == False:
                break 
            
            # Need to decode the clients message since its distributed in bytes form
            clientMessage = decode(data) 
            handleMessage(client, clientMessage["type"], clientMessage["data"])

    except Exception as e: 

        broadcast("SERVER END",0)

        playerLeft = True

        endConnectionServer()
    
# Handles provided message by the client
def handleMessage(client,messageType,data):
    
    # Client joins game 
    if messageType == "JOIN GAME":
        addPlayer(client,data)   
        # Register player

    # Client submits answer
    elif messageType == "SUBMIT":
        global submittedPlayers
        submittedPlayers.append(data)
        tellClientsSubmittedPlayers()

    # Client sends their stats
    if messageType == "PLAYER STATS":
        global dataSent
        global questionsCorrect

        if data["ID"] not in questionsCorrect:
            questionsCorrect[data["ID"]] = []

        # If correct then these stats are updated
        if data["isCorrect"] == "Correct":
            connectedPlayers[data["ID"]]["isCorrect"] = "Correct"
            connectedPlayers[data["ID"]]["timing"] = data["timing"]
            connectedPlayers[data["ID"]]["points"] = data["points"]
        else:
            connectedPlayers[data["ID"]]["isCorrect"] = "Incorrect"
            connectedPlayers[data["ID"]]["timing"] = data["timing"]

        questionsCorrect[data["ID"]].append(data["isCorrect"])
        dataSent += 1

# Adds client
def addPlayer(client,data):

    if len(clients) == 3:
        client.send(encode("FULL",0))

    elif hasStarted:
        client.send(encode("IN PROGRESS",0))
    
    else:
        # Forms the client ID based on the elements in the list
        clientID = len(clients) 

        # Makes a dictionary containing client ID and assigns a playerID
        clients[clientID] = [client] 

        connectedPlayersID = len(connectedPlayers)

        # Adds all information of that client
        connectedPlayers[connectedPlayersID] = {
            "name": data["name"],
            "points": 0,
            "equippedItem": data["equippedItem"],
            "timing": None,
            "isCorrect": None
        } 
        client.send(encode("PLAYER ID",connectedPlayersID))

# Checking if clients are still connected
def checkClients():
    global playerLeft

    if playerLeft:
        broadcast("SERVER END",0)

        endConnectionServer()
        return(True)
    else:
        return(False)

# Resets all global Variables for next connection
def endConnectionServer():
    global clients, connectedPlayers, dataSent, submittedPlayers, questionsCorrect, hasStarted

    hasStarted = False

    # Stores the player id of all the clients so this can be fetched
    clients = {} 

    # Stores the player information of all the players in game
    connectedPlayers = {} 

    dataSent = 0

    submittedPlayers = []

    questionsCorrect = {}

    server.close()

# Alerts the client of the game starting
def startGame(questionids): 
    global connectedPlayers, hasStarted

    # Sends question ids
    broadcast("QUESTION IDS",{"questionids": questionids})

    # Sends connected user
    broadcast("PLAYERS CONNECTED",{"players": connectedPlayers})

    hasStarted = True

# Broadcasts a message to all connected clients
def broadcast(messageType,data):

    # Cycles through all clients and sends a message to all the clients 
    for information in clients.values():
        client = information[0]

        try:
            client.send(encode(messageType, data))

        except Exception as e:
            print(f"Exception",e)


# Updates the servers time 
def updateTime(isCorrect,timing, points):
    if isCorrect == "Correct":
        connectedPlayers[0]["timing"] = timing
        connectedPlayers[0]["isCorrect"] = "Correct"
        connectedPlayers[0]["points"] = points
    else:
        connectedPlayers[0]["isCorrect"] = "Incorrect"
        connectedPlayers[0]["timing"] = timing


def pointsCalculator():
    global connectedPlayers
    
    timeComparer = []
    
    # Searches through all connected players
    for key, value in connectedPlayers.items():
        if value["isCorrect"] == "Correct":
            timeComparer.append({
                "ID": key,
                "timing": value["timing"]
            })

    # Checks if the list is present
    if timeComparer:

        # Sorts by Ascending
        timeComparer.sort(key = lambda fastest: fastest["timing"])
        quickestPlayer = timeComparer[0]["ID"]
        connectedPlayers[quickestPlayer]["points"] += 3
                
    # Sends all clients the server stats       
    broadcast("SERVER STATS", connectedPlayers)

# Checks if all clients have sent their statistics (before sending the server stats to everyone)       
def dataSentCheckerServer():
    global dataSent

    if dataSent == len(clients):
        dataSent = 0
        return True
    else:
        return False

# Retrieves the player score
def retrievePlayersServer():

    global connectedPlayers

    tempConnectedPlayers = connectedPlayers.copy()

    # On server index is int but on client this same function is string due to json converting to strings 
    tempConnectedPlayers.pop(0)
    return tempConnectedPlayers

# Submits answer as a server and alerts other clients
def submitAnswerServer():
    global submittedPlayers

    submittedPlayers.append(0)

    tellClientsSubmittedPlayers()

# Checks if all players have clicked the submit button
def checkAllPlayerSubmit():

    if len(submittedPlayers) == len(connectedPlayers) and playerLeft == False:

        broadcast("ROUND END", 0)

        return ("End Round")

    elif playerLeft == True:
        return ("Left")

    else:
        return ("Continue")

# Tells all the clients who has submitted
def tellClientsSubmittedPlayers():
    global submittedPlayers
    broadcast("SUBMITTED PLAYERS",submittedPlayers)

# Checks the submitted players as a server
def checkSubmittedPlayersServer():
    global submittedPlayers
    
    return submittedPlayers

# Resets the submitted player (after a round has finished)
def resetSubmittedPlayersServer():
    global submittedPlayers

    submittedPlayers = []

# Obtains the players score as the server
def retrievePlayerScoreServer():
    global connectedPlayers

    return (connectedPlayers[0]["points"]) 

# Sends clients all the questions they have gotten correct
def sendClientsQuestionsCorrect():
    global questionsCorrect

    broadcast("QUESTIONS CORRECT",questionsCorrect)

# Checks if the player is correct as the server 
def isPlayerCorrectServer():
    return connectedPlayers[0]["isCorrect"]

