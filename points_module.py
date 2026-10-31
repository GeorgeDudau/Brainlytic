import sqlite3

# Creates the shop items tables
def createShopItems():
    # Connects to the database containing items with their respective prices

    connect = sqlite3.connect("shopItems.db")

    cursor = connect.cursor()

    # Creates the table in which the items will be store in
    itemsCreate = "CREATE TABLE IF NOT EXISTS " \
    "shopItems(itemid INTEGER PRIMARY KEY,name TEXT NOT NULL, type TEXT NOT NULL , price INTEGER NOT NULL)"
    cursor.execute(itemsCreate)

    # Inserts default catalog of all items available (This will be edited later on if the user chooses to purchase items)
    # INSERT OR IGNORE prevents any data duplicates in case this code is executed again

    items =[
    (0,"Blue Nametag","name_tag",50),
    (1,"Red Nametag","name_tag",60),
    (2,"Yellow Nametag","name_tag",75),
    (3,"Green Nametag","name_tag",85),
    (4,"Pink Nametag","name_tag",100),
    (5,"Purple Nametag","name_tag",150),
    (6,"Male Mathematician","profile_picture",50),
    (7,"Female Mathematician","profile",50),
    (8,"Physics", "profile_picture", 50),
    (9,"Chemistry", "profile_picture", 50),
    (10,"Biology", "profile_picture", 50),
    (11,"Einstein", "profile_picture", 75),
    (12,"Cringeman", "profile_picture", 100),
    (13,"Greek Alphabet", "profile_picture", 175),
    (14,"Golden Fish", "profile_picture", 200)]

    cursor.executemany("INSERT OR IGNORE INTO shopItems (itemid,name,type,price) VALUES (?,?,?,?)",
                       items)
    # Saves and closes database
    connect.commit()
    connect.close()

# Creates the progress tables (used to track user progress)
def createProgressTable():
    # Connects to the progress data base
    connect = sqlite3.connect("progress.db")

    cursor = connect.cursor()

    # Creates an intermediatery table for which items the user owns
    progressCreate = "CREATE TABLE IF NOT EXISTS " \
    "progress(userid INTEGER, itemid INTEGER, equipped INTEGER DEFAULT 0," \
    "PRIMARY KEY (userid, itemid)," \
    "FOREIGN KEY (userid) REFERENCES credentials(userid)," \
    "FOREIGN KEY (itemid) REFERENCES shopItems(itemid))"
    
    # Executes command
    cursor.execute(progressCreate)
    
    # Saves and closes database
    connect.commit()
    connect.close()

# Purchases Item 
def purchaseItem(userid,itemid):

    # Connects to credentials database
    connectCredentials = sqlite3.connect("credentials.db")
    cursorCredentials = connectCredentials.cursor()

    userPoints = getUserPoints(userid)

    # Fetches the price of the item the user wishes to buy
    connectshopItem = sqlite3.connect("shopItems.db")
    cursorshopItem = connectshopItem.cursor()
    priceFetch = "SELECT price FROM shopItems WHERE itemid = ?"

    # Fetches the Price and stores it 
    cursorshopItem.execute(priceFetch, (itemid,))
    itemPrice = cursorshopItem.fetchone()[0]
    connectshopItem.commit()
    connectshopItem.close()

    # Checks to see if the user has enough points
    if userPoints < itemPrice:
        return(False)
    else:
        # Updates the users balance after purchasing the item
        userPoints = userPoints - itemPrice

        # Connects to credentials database
        connectCredentials = sqlite3.connect("credentials.db")
        cursorCredentials = connectCredentials.cursor()

        # Stores new point balance in a database
        pointsDeduction = "UPDATE credentials " \
        "SET points = ? WHERE userid = ?"
        cursorCredentials.execute(pointsDeduction,(userPoints, userid,))
        connectCredentials.commit()

        # Connects to progress database
        connectProgess = sqlite3.connect("progress.db")
        cursorProgress = connectProgess.cursor()

        # Inserts the purchased item into a progress database
        newItemInsert = "INSERT INTO progress (userid, itemid) VALUES(?,?)"

        cursorProgress.execute(newItemInsert, (userid,itemid,))
        connectProgess.commit()
        connectProgess.close()
        return(True)

# Fetches the users' points
def getUserPoints(userid):

    # Connects to credentials database
    connectCredentials = sqlite3.connect("credentials.db")
    cursorCredentials = connectCredentials.cursor()

    # Fetches the users points stored in the database
    pointsFetch = "SELECT points FROM credentials WHERE userid = ?"
    cursorCredentials.execute(pointsFetch,(userid,))
    userPoints = cursorCredentials.fetchone()[0]

    # Ends connection with databases as they are now unneeded
    connectCredentials.close()
    return userPoints

# Gets the users items
def getUserItems(userid):

     # Connects to progress database
    connectProgress = sqlite3.connect("progress.db")
    cursorProgress = connectProgress.cursor()
    # Fetches the items owned by the user
    itemFetch = "SELECT itemid FROM progress WHERE userid = ?"
    cursorProgress.execute(itemFetch, (userid,))
    
    #Items stored in a 2D array
    itemsOwned = cursorProgress.fetchall()

    # Converts the array into 1D with just the ids
    itemsOwned = [item[0] for item in itemsOwned]
    connectProgress.close()

    # Checks to see if user owns any items.
    if not itemsOwned:
        return(False)
    else:
        return itemsOwned
    
# Equips the users requested item
def equipItem(userid,itemid):

    # Connects to progress database
    connectProgress = sqlite3.connect("progress.db")
    cursorProgress = connectProgress.cursor()

    # Sets previously equipped item to 0 so its not longer equipped
    removeEquipStatus = "UPDATE progress SET equipped = 0 WHERE userid = ? AND equipped = 1"

    # Sets new item to be equipped
    updateItem = "UPDATE progress SET equipped = 1 WHERE userid = ? AND itemid = ?"
    cursorProgress.execute(removeEquipStatus,(userid,))
    cursorProgress.execute(updateItem, (userid, itemid,))
    connectProgress.commit()
    connectProgress.close()

    return itemid

# Finds the equipped item 
def findEquippedItem(userid):
    # Connects to progress database
    connectProgress = sqlite3.connect("progress.db")
    cursorProgress = connectProgress.cursor()

    # Searches for the users current equipped item 
    searchEquippedItem = "SELECT itemid FROM progress WHERE equipped = 1 AND userid = ?"

    cursorProgress.execute(searchEquippedItem, (userid,))
    result = cursorProgress.fetchone()

    connectProgress.close()
    
    if result is not None:  
        return result[0]
    else:
        return None

# Unequips the selected item
def unequipItem(userid,itemid):

    # Connects to progress database
    connectProgress = sqlite3.connect("progress.db")
    cursorProgress = connectProgress.cursor()

    # Sets previously equipped item to 0 so its not longer equipped
    removeEquipStatus = "UPDATE progress SET equipped = 0 WHERE userid = ? AND equipped = 1"
    cursorProgress.execute(removeEquipStatus,(userid,))
    connectProgress.commit()
    connectProgress.close()

# Adds the points the user has earned in a match

def addPoints(userid,addedPoints):

    # Connects to progress database
    connectProgress = sqlite3.connect("credentials.db")
    cursorProgress = connectProgress.cursor()

    # Adds the new points to the points previously in the database
    points = getUserPoints(userid)
    points += addedPoints
    
    # Actually adds the points to the database
    addPoints = "UPDATE credentials SET points = ? WHERE userid = ?"
    cursorProgress.execute(addPoints,(points, userid,))
    connectProgress.commit()
    connectProgress.close()

