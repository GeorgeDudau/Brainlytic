#This connects UI to Logic
# Needed for Format Checking
import sys
import re
import time

# Needed for bots in singleplayer mode
import random

# Imports Functions from other files
from auth_module import loginProcess, signupProcess, createSession, fetchUserID, existingEmailCheck, fetchUserName
from points_module import createShopItems, createProgressTable, purchaseItem, getUserPoints, getUserItems, equipItem, findEquippedItem, unequipItem, addPoints
from question_module import questionDatabase, questionRetrieval, mathAnswerChecker, questionRetrievalID

# Imports the main GUI
from ui_main import userInterface
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

# Queues
from collections import deque

# Imports access to variables and functions within the server module
import server
from server import acceptClients, startGame ,startServer, updateDetails, updateTime, pointsCalculator, dataSentCheckerServer, retrievePlayersServer, submitAnswerServer, checkAllPlayerSubmit, checkSubmittedPlayersServer,retrievePlayerScoreServer, resetSubmittedPlayersServer, sendClientsQuestionsCorrect, isPlayerCorrectServer,checkClients,endConnectionServer # Imports the class from server .py

# Imports access to variables and functions within the client module
import clientModule
from clientModule import connect,fetchQuestionidsFromServer, updateStats, dataSentCheckerClient, retrievePlayersClient, tellServerSubmitAnswer, checkSubmittedPlayersClient,retrievePlayerScoreClient, resetSubmittedPlayersClient, isPlayerCorrectClient, retrievePlayerID, roundInProgress, checkServer,endConnectionClient

# Allows concurrent processing 
import threading 

# Main Application Class
class Application(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

    # Instance of UI elements created in class
        self.ui = userInterface()
        self.ui.setupUi(self)

        # Assigning the function of each button 

        # Auth Module Buttons

        # Login button
        self.ui.loginButton.clicked.connect(self.handleLogin)
        # To signup page button from login page
        self.ui.dontHaveAccountButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(9))
        # Signup button
        self.ui.signupButton.clicked.connect(self.handleSignup)
        # Hides the warning labels in login pages
        self.ui.loginStatus.hide()
        self.ui.signupStatus.hide()

        # Navigation Buttons

        # To login page button from signup page
        self.ui.alreadyHaveAnAccount.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(11))
        # To login page from email verification page 
        self.ui.backButtonEmailConfirmation.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(9))
        # To shop from home page
        self.ui.Shop.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        # To home page from shop
        self.ui.backButtonShop.clicked.connect(lambda:self.ui.stackedWidget.setCurrentIndex(0))
        # To homepage from profile
        self.ui.backButtonProfile.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        # To mode selection from home page (singleplayer)
        self.ui.SinglePlayer.clicked.connect(self.selectSinglePlayer)
        # To mode selection from home page (multiplayer)
        self.ui.Multiplayer.clicked.connect(self.selectMultiPlayer)
        # To home page from mode selection
        self.ui.backButtonPaperSelection.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        # To home page from score page
        self.ui.backButtonScore.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        # To home page from multiplayer page
        self.ui.backButtonMultiPlayerServerMenu.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        # To home Page from multiplayer connecting page
        self.ui.backButtonServer.clicked.connect(lambda: self.leaveConnecting())


        self.ui.multiBottomLine3.hide()
        self.ui.forfeitSingle.clicked.connect(self.timeStopForfeitSP)
        
    # Shop Buttons
        # Nametags 
        self.ui.bluePurchase.clicked.connect(lambda: self.purchaseConfirmation(0))
        self.ui.redPurchase.clicked.connect(lambda: self.purchaseConfirmation(1))
        self.ui.yellowPurchase.clicked.connect(lambda: self.purchaseConfirmation(2))
        self.ui.greenPurchase.clicked.connect(lambda: self.purchaseConfirmation(3))
        self.ui.pinkPurchase.clicked.connect(lambda: self.purchaseConfirmation(4))
        self.ui.purplePurchase.clicked.connect(lambda: self.purchaseConfirmation(5))
        # Icons
        self.ui.mathMaleIcon.clicked.connect(lambda: self.purchaseConfirmation(6))
        self.ui.mathFemaleButton.clicked.connect(lambda: self.purchaseConfirmation(7))
        self.ui.physicsPurchase.clicked.connect(lambda: self.purchaseConfirmation(8))
        self.ui.biologyPfpPurchase.clicked.connect(lambda: self.purchaseConfirmation(9))
        self.ui.chemistryPfpPurchase.clicked.connect(lambda: self.purchaseConfirmation(10))
        self.ui.einsteinPfpPurchase.clicked.connect(lambda: self.purchaseConfirmation(11))
        self.ui.cringeManPurchase.clicked.connect(lambda: self.purchaseConfirmation(12))
        self.ui.AlphaOmegaPurchase.clicked.connect(lambda: self.purchaseConfirmation(13))
        self.ui.fisherofmenPurchase.clicked.connect(lambda: self.purchaseConfirmation(14))
    
# Mode selection buttons

        self.ui.math2017Button.clicked.connect(lambda: self.playerMode(self.selectedMode,"2017","math"))
        self.ui.math2018Button.clicked.connect(lambda: self.playerMode(self.selectedMode,"2018","math"))
        self.ui.math2019Button.clicked.connect(lambda: self.playerMode(self.selectedMode,"2019","math"))
        self.ui.math2020Button.clicked.connect(lambda: self.playerMode(self.selectedMode,"2020","math"))
        self.ui.math2021Button.clicked.connect(lambda: self.playerMode(self.selectedMode,"2021","math"))
        self.ui.math2022Button.clicked.connect(lambda: self.playerMode(self.selectedMode,"2022","math"))

# Multiplayer buttons
    # Hosts game
        self.ui.hostButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(3))
    # Joins game
        self.ui.joinButton.clicked.connect(lambda: self.joinGame())
# Main Game buttons
    # Submit button (singleplayer)
        self.ui.submitSingle.clicked.connect(lambda: self.submitAnswerSP())
    # Submit button (multiplayer)
        self.ui.submitMulti.clicked.connect(lambda: self.submitAnswerMP())

# All necessary data structures and connections are assigned here

    # Assigning the sessions dictionary
        self.sessions = {}
        # Collection of all shop buttons avaliable
        
        self.shopButtons = {
            0: self.ui.bluePurchase,
            1: self.ui.redPurchase,
            2: self.ui.yellowPurchase,
            3: self.ui.greenPurchase,
            4: self.ui.pinkPurchase,
            5: self.ui.purplePurchase,
            6: self.ui.mathMaleIcon,
            7: self.ui.mathFemaleButton,
            8: self.ui.physicsPurchase, 
            9: self.ui.biologyPfpPurchase,
            10: self.ui.chemistryPfpPurchase,
            11: self.ui.einsteinPfpPurchase,
            12: self.ui.cringeManPurchase, 
            13: self.ui.AlphaOmegaPurchase,
            14: self.ui.fisherofmenPurchase, 
        }

        # Indicates the mode the player has selected
        self.selectedMode = None      
        self.isClient = False
        self.isServer = False
        self.userPoints = 0
        self.statsSent = 0
    ## Beginning of Authentication Logic ##

    # Handles logging into an existing account
    def handleLogin(self):

        # Takes Email Address and Password
        emailAddress = self.ui.emailAddressLogin.toPlainText()
        password = self.ui.passwordLogin.toPlainText()

        # Sets a flag
        errorFound = False

        # Checks if email field are empty
        if self.isEmpty(emailAddress):
            self.ui.loginStatus.setText("Please enter your email address")
            self.ui.loginStatus.show()
            errorFound = True
        # Checks if password field is empty
        if self.isEmpty(password):
            self.ui.loginStatus.setText("Please enter a password")
            self.ui.loginStatus.show()
            errorFound = True

        # Checks if credentials given match data in database
        if errorFound == False:
            if loginProcess(emailAddress,password):
                
                # Fetches user ID
                userid = fetchUserID(emailAddress)

                # Creates a session token 
                self.token = createSession(userid,self.sessions)

                # Restores functions of buttons in the shop
                self.updateShopButtonsFunctions(userid)

                # Updates all points labels
                self.pointsUpdater(userid)


                # Switches to home page
                self.ui.stackedWidget.setCurrentIndex(0)

                self.ui.connectingPlayerText.setText(fetchUserName(userid))
            # Warn user of invalid password
            else:
                self.ui.loginStatus.setText("Invalid email address or password")
                self.ui.loginStatus.show()


    
    # Function to determine if a text box is empty
    def isEmpty(self,data):
        return not(data.strip())
    
    # Checks if the email is in the correct format (@gmail.com)
    def validEmailCheck(self,email):

        # Standard Email Format
        format = r'^[a-zA-Z0-9._]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'

        # Checks if email is in the correct format
        if re.match(format,email):
            return(True)
        else:
            return(False)
        

    # Handles making a new account
    def handleSignup(self):

        # Takes the 4 inputs from the fields
        fullName = self.ui.fullNameSignup.toPlainText()
        emailAddress = self.ui.emailaddressSignup.toPlainText()
        password = self.ui.passwordSignup.toPlainText()
        passwordConfirmation = self.ui.confirmPasswordSignup.toPlainText()

        # Sets a flag
        errorFound = False
        
        # Checks if Full Name field is empty
        if self.isEmpty(fullName):
            self.ui.signupStatus.setText("Please enter your Full Name")
            self.ui.signupStatus.show()
            errorFound = True

        # Checks if Email field is empty
        if self.isEmpty(emailAddress):
            self.ui.signupStatus.setText("Please enter your email address")
            self.ui.signupStatus.show()
            errorFound = True

        # Checks if Full Name field is empty
        if self.isEmpty(password):
            self.ui.signupStatus.setText("Please enter a password")
            self.ui.signupStatus.show()
            errorFound = True


        # Checks if password and password confirmation field are identical
        if password != passwordConfirmation:
            self.ui.signupStatus.setText("Passwords do not match")
            self.ui.signupStatus.show()
            errorFound = True

        #Checks email formatting
        if not self.validEmailCheck(emailAddress):
            self.ui.signupStatus.setText("Please ensure that your email is in the correct format")
            self.ui.signupStatus.show()
            errorFound = True

        # Checks if email doesnt already exists
        if existingEmailCheck(emailAddress):
            self.ui.signupStatus.setText("An account already exists with the email provided")
            self.ui.signupStatus.show()
            errorFound = True

        # If a flag is raised then the function is not executed
        if not errorFound:
            
            # Keeps variables email Address and fullName self contained avoiding global variable
            self.signupEmail = emailAddress
            self.signupName = fullName
            self.signupPassword = password


            self.demoHandler()


    def passwordStrengthCheck(self, password):

        # Checks if password is less than 8 characters
        if len(password) < 8:
            return False
        
        # Checks if capital letters are present
        if not re.search(r"[A-Z]", password):
            return False
        
        # Checks if lowercase letters are present
        if not re.search(r"a-z", password):
            return False
        
        # Checks if any numbers are present
        if not re.search(r"0-9", password):
            return False
        
        # Checks if special characters are present
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        
        # If all are cases are fufilled
        return True

# Handles email verification
    def demoHandler(self):
        # Creates an account
        signupProcess(self.signupName,self.signupEmail,self.signupPassword)

        # Gets user ID
        userid = fetchUserID(self.signupEmail)

        # In case the user has deleted the previous databases (All database use CREATE IF NOT EXISTS)
        createProgressTable()
        createShopItems()
        questionDatabase()

        # Updates all buttons and labels 
        self.updateShopButtonsFunctions(userid)
        self.pointsUpdater(userid)

        # Create a session
        self.token = createSession(userid,self.sessions)

        # Changes page to home page
        self.ui.stackedWidget.setCurrentIndex(0)





## End of Authentication Logic ##

# Handles the Purchase logic    
    def purchaseConfirmation(self,itemid):

        # Fetches the dictionary value for userid
        userid = self.sessions[self.token]["userid"]

        # Checks to see if the purchase has gone through.
        if purchaseItem(userid,itemid):
            self.updateShopButtonsFunctions(userid)
            self.pointsUpdater(userid)

        # Warns the user of insufficient funds
        else:
            text = "You have insufficient funds."
            self.warningPopup(text)



# Updates all points labels (may be executed multiple times a session so kept seperate)   
    def pointsUpdater(self,userid):
        # Fetches the users points
        points = getUserPoints(userid)

        # Updates points labels in the home page
        self.ui.pointsMainPage.setText(f"Points: {points}")
        # Updates points labels in the shop page
        self.ui.pointsLabel.setText(f"Points: {points}")



# Updates the text shown on the buttons in the shop
    def shopButtonEquip(self,userid,itemid):

        # Takes in user items array
        userItems = getUserItems(userid)

        # Equips the desired item (Updates the database)
        equippedItem = equipItem(userid,itemid)

        # Searches through all bought items
        for item in userItems:

            # If the item is not equipped then its label is updated to hold equip
            if item != equippedItem:

            # Label indicating owned by unequipped labels.
                self.shopButtons[item].setText("Equip")
                
            # Label indicating equipped item
            else:
                self.shopButtons[item].setText("Equipped")
                button = self.shopButtons[item]
                # Prevents crashing in case the button has no connection
                try:
                    button.clicked.disconnect()
                except TypeError:
                    pass

                # Assigns each button with their respective item ids and functions
                button.clicked.connect(lambda _, specificItem = item: self.shopButtonUnequip(userid,specificItem)) 



    # Allows the item to be unequipped 
    def shopButtonUnequip(self,userid,itemid):

        # Unequips the item
        unequipItem(userid,itemid)

        # Assigns variable the equipped button
        button = self.shopButtons[itemid]

        # Disconnects previous function
        button.clicked.disconnect()

        # Connects new function
        button.clicked.connect(lambda _, specificItem = itemid: self.shopButtonEquip(userid,specificItem))

        # Updates text
        self.shopButtons[itemid].setText("Equip")



# Updates functions of buttons associated with items already bought
    def updateShopButtonsFunctions(self, userid):
        # Takes in user items array
        userItems = getUserItems(userid)

        # If false (meaning no items present) then return false
        if userItems == False:
            return False
        
        else:
            equippedItem = findEquippedItem(userid)

            # For loop to cycle through all the owned items 
            for item in userItems:
                button = self.shopButtons[item]

                # Updates the button text depending on if the button is equipped or not
                if item != equippedItem:
                    button.setText("Equip")
                else:
                    button.setText("Equipped")

                # Prevents crashing in case the button has no connection
                try:
                    button.clicked.disconnect()
                except TypeError:
                    pass

                # Assigns each button with their respective item ids and functions
                button.clicked.connect(lambda _, specificItem = item: self.shopButtonEquip(userid,specificItem)) 



    # Displays a warning popup 
    def warningPopup(self,text):
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText(text)
        msg.setIcon(QMessageBox.Warning)
        msg.exec_()

## End of Points Logic ##
    # Checks the selected mode by the user 
    def playerMode(self,playerMode,selectedYear,subject):
        if playerMode == "singleplayer":
            self.yearSelectSP(selectedYear,subject)
        else:
            self.hostGame(selectedYear)


## Start of Game logic##

    # Selects the single player mode and navigates to mode selection page.
    def selectSinglePlayer(self):
        self.selectedMode = "singleplayer"
        self.ui.stackedWidget.setCurrentIndex(3)


    
    # Displays a popup window to ensure that the user is ready to play the game
    def playConfirmationPopup(self,text):

        # Contents of the popup
        msg = QMessageBox()
        msg.setWindowTitle("Game Start")
        msg.setText(text)
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No )
        msg.setDefaultButton(QMessageBox.Yes)

        # Records the users response
        response = msg.exec()

        # Checks user response
        if response == QMessageBox.Yes:
            return True
        else:
            return False
    

    # Checks the year selected
    def yearSelectSP(self,selectedYear, subject):
        match subject:
            case "math":
                # Retrieves the 3 questions used per round (randomly selected)
                
                questions = questionRetrieval(selectedYear)
                self.selectedSubject = "math"
                
                # Sets the number of rounds
                self.rounds = 3

                # Switches to main game
                self.ui.stackedWidget.setCurrentIndex(7)

                # Allows the player to decide if they are ready 
                readyToPlay = self.playConfirmationPopup("Are you ready to start the game?")

                # Checks if the user is ready to play
                if readyToPlay:
                    # Makes a queue and adds all questions to that queue
                    self.questionQueue = deque()
                    for q in questions:
                        self.questionQueue.append(q)

                    # Removes first item in queue and assigns temporary variables
                    (questionID,year,imagePath,markschemePath,correctAnswer,marks,timing,questionType) = self.questionQueue.popleft()

                    # Total points obtained during a match
                    self.matchPoints = 0

                    # Allows variables to be accessed
                    self.currentImagePath = QtGui.QPixmap(imagePath)
                    self.currentMarkSchemePath = QtGui.QPixmap(markschemePath)
                    self.currentCorrectAnswer = correctAnswer
                    self.currentMarks = marks
                    self.currentQuestionType = questionType
                    self.maxTiming = timing

                    # Shows displays for 4 players (if previous round was multiplayer and had  < 3 players)
                    self.ui.player1TextSingle_40.show()
                    self.ui.player1TextSingle_41.show()
                    self.ui.player1TextSingle_45.show()
                    self.ui.player1TextSingle_43.show()
                    self.ui.player1TextSingle_44.show()
                    self.ui.player1TextSingle_50.show()
                    self.ui.player1TextSingle_47.show()
                    self.ui.player1TextSingle_51.show()

                    self.ui.player3TextSingle.show()
                    self.ui.player3IconSingle.show()

                    self.ui.player1TextSingle_55.show()
                    self.ui.player1TextSingle_59.show()
                    self.ui.player1TextSingle_58.show()
                    self.ui.player1TextSingle_53.show()
                    self.ui.player1TextSingle_60.show()
                    self.ui.player1TextSingle_56.show()
                    self.ui.player1TextSingle_61.show()
                    self.ui.player1TextSingle_52.show()
                    
                    self.ui.player4IconSingle.show()
                    self.ui.player4TextSingle.show()
                    
                    # Displays question
                    self.ui.mainS.setPixmap(self.currentImagePath)

                    # Progress bar setup
                    self.progressBar = 0
                    
                    # Starts the question timer
                    self.startQuestionTimerSP(timing)

                    # Creates a dictionary of all the bots in game
                    self.bots = {}

                    self.addBot(0) # Add bot 1
                    self.addBot(1) # Add bot 2
                    self.addBot(2) # Add bot 3
 
                    # Starts the timer until the bot submit their answer
                    self.startBotTimer(0,self.bots[0]["timing"])
                    self.startBotTimer(1,self.bots[1]["timing"])
                    self.startBotTimer(2,self.bots[2]["timing"])

                    # Sets the bots profile picture
                    self.botPicture()

                    # Tracks the correct questions for the players
                    self.userCorrect = []
                    self.bot1Correct = []
                    self.bot2Correct = []
                    self.bot3Correct = []

                    self.setCosmetics(self.sessions[self.token]["userid"])
                else:
                    # returns to selection page
                    self.ui.stackedWidget.setCurrentIndex(3)


            


    # Begins the question timer
    def startQuestionTimerSP(self,time):

        # Sets the maximum timer count and the timer
        self.questionTimerCount = time
        self.questionTimer = QtCore.QTimer(self)

        # Assigns a function once the timer is stopped
        self.questionTimer.timeout.connect(self.updateQuestionTimerSP)

        # Updates timer every 1 second
        self.questionTimer.start(1000)



    # Updates the labels and timer every second
    def updateQuestionTimerSP(self):

        # Minute and seconds display
        minutes = self.questionTimerCount //  60
        seconds = self.questionTimerCount % 60
        if seconds <= 9:
            self.ui.singleTimer.setText(f"{minutes}:0{seconds}")   
        else:
            self.ui.singleTimer.setText(f"{minutes}:{seconds}")   

        #Decrements timer
        self.questionTimerCount -= 1
        
        #Increments progressBar
        self.progressBar += 100/(self.maxTiming)

        # Sometimes the bar exeeds 100 percent due to rounding
        if self.progressBar > 100:
            self.progressBar = 100

        # Sets value of test progress
        self.ui.testProgress.setValue(int(self.progressBar))

        # Stops timer if time runs out
        if self.questionTimerCount < 0:
            self.timeUpSP()
    


    # Button when the user is finished.
    def submitAnswerSP(self):
        self.timeUpSP()


    def timeStopForfeitSP(self):
        # Stops the timer 
        self.questionTimer.stop()

        self.ui.bot1Timer.stop()

        self.ui.bot2Timer.stop()

        self.ui.bot3Timer.stop()

        self.ui.stackedWidget.setCurrentIndex(0)


    # Function when time is up
    def timeUpSP(self):

        # Stops the timer 
        self.questionTimer.stop()

        self.stopBotTimer()

        # Record the users time 
        self.completionTime = self.maxTiming - self.questionTimerCount

        # Decrements the number of rounds
        self.rounds -= 1

        # Goes to mark scheme page
        self.ui.stackedWidget.setCurrentIndex(4)

        # Shows the mark scheme
        self.ui.markSchemeImage.setPixmap(self.currentMarkSchemePath)

        # Converts user answer to text
        userAnswer = self.ui.inputS.toPlainText()
        self.ui.userAnswerLabel.setText(userAnswer)

        # Checks the selected subject to retrieve the correct comparison method
        if self.selectedSubject == "math":
            scoreList = []

            # Checks to see if the user answers are correct
            if mathAnswerChecker(userAnswer,self.currentCorrectAnswer,self.currentQuestionType):
                userCorrect = "Correct"
                # Awards full marks
                userPoints = self.currentMarks
                # The user has got it correct so his timing is added to the time comparison list
                scoreList.append({"type": "user", "timing": self.completionTime})

                # Checks every bot to see if they have got the answer correct
                for index, bot in (self.bots.items()):
                    if bot["isCorrect"] == "Correct":
                        # Adds full marks to the bots total
                        self.bots[index]["points"] += self.currentMarks

                        # Adds to the time comparison list
                        scoreList.append({
                            "type": index,
                            "timing": self.bots[index]["timing"]
                        })

                # Checks if the list is present
                if scoreList:
                    # Sorts by Ascending
                    scoreList.sort(key = lambda fastest: fastest["timing"])

                    # Smallest time wins 
                    winner = scoreList[0]

                    # Checks if the winner is the user
                    if winner["type"] == "user":
                        bonus = 3
                        userPoints += 3

                    # Checks if the winner is a bot
                    else:
                        bonus = 0
                        botid = winner["type"]
                        self.bots[botid]["points"] += 3

                # Adds match points 
                self.matchPoints += userPoints

                # Displays the score status of the round
                self.ui.userPointsLabel.setText( f"You have gained {userPoints} Points\n"
                    f"Total points: {self.matchPoints}\n"
                    f"Bonus: {bonus} \n"
                    f"{self.bots[0]['name']}: {self.bots[0]['points']} Points\n"
                    f"Answer: {self.bots[0]['isCorrect']} completed in "
                    f"{self.bots[0]['timing'] // 60} minutes and {self.bots[0]['timing'] % 60} seconds\n"
                    f"{self.bots[1]['name']}: {self.bots[1]['points']} Points\n"
                    f"Answer: {self.bots[1]['isCorrect']} completed in "
                    f"{self.bots[1]['timing'] // 60} minutes and {self.bots[1]['timing'] % 60} seconds\n"
                    f"{self.bots[2]['name']}: {self.bots[2]['points']} Points\n"
                    f"Answer: {self.bots[2]['isCorrect']} completed in "
                    f"{self.bots[2]['timing'] // 60} minutes and {self.bots[2]['timing'] % 60} seconds")
                
            # If the user doesnt get the answer
            else:
                userPoints = 0
                userCorrect = "Incorrect"

                # Checks every bot to see if they have got the answer correct
                for index, bot in (self.bots.items()):
                    if bot["isCorrect"] == "Correct":

                        # Adds full marks to the bots total
                        self.bots[index]["points"] += self.currentMarks

                        # Adds to the time comparison list
                        scoreList.append({
                            "type": index,
                            "timing": self.bots[index]["timing"]
                        })

                # Checks if the list is present
                if scoreList:

                    # Sorts by Ascending
                    scoreList.sort(key = lambda fastest: fastest["timing"])

                    # Smallest time wins 
                    winner = scoreList[0]

                    # Adds the score
                    botid = winner["type"]
                    self.bots[botid]["points"] += 3

                # Displays the score status of the round
                self.ui.userPointsLabel.setText(f"You have gained 0 Points\n"
                f"Total points: {self.matchPoints}\n"
                f"{self.bots[0]['name']}: {self.bots[0]['points']} Points\n"
                f"Answer: {self.bots[0]['isCorrect']} completed in "
                f"{self.bots[0]['timing'] // 60} minutes and {self.bots[0]['timing'] % 60} seconds\n"
                f"{self.bots[1]['name']}: {self.bots[1]['points']} Points\n"
                f"Answer: {self.bots[1]['isCorrect']} completed in "
                f"{self.bots[1]['timing'] // 60} minutes and {self.bots[1]['timing'] % 60} seconds\n"
                f"{self.bots[2]['name']}: {self.bots[2]['points']} Points\n"
                f"Answer: {self.bots[2]['isCorrect']} completed in "
                f"{self.bots[2]['timing'] // 60} minutes and {self.bots[2]['timing'] % 60} seconds")
            
            # Adds whether the user has got a question correct or in incorrect to an array
            self.userCorrect.append(userCorrect)
            self.bot1Correct.append(self.bots[0]["isCorrect"])
            self.bot2Correct.append(self.bots[1]["isCorrect"])
            self.bot3Correct.append(self.bots[2]["isCorrect"])

            # Sets intermission timer
            QtCore.QTimer.singleShot(10000,self.intermissionTimerSP)




    # Time before next round begins
    def intermissionTimerSP(self):

        # Asks the user if they want to continue onto the next round
        confirmed = self.playConfirmationPopup("Would you like to continue?")
        
        # If would like to continue
        if confirmed:
            # If no more rounds move to end page
            if self.rounds == 0:
                self.endRoundSP()
            # Move to next round
            else:
                self.nextRound()
        else:
            # Restarts timer 
            QtCore.QTimer.singleShot(10000,self.intermissionTimerSP)



    # Switches to next round
    def nextRound(self):
        # Switches to main game
            self.ui.stackedWidget.setCurrentIndex(7)

         # Removes first item in queue and assigns temporary variables
            (questionID,year,imagePath,markschemePath,correctAnswer,marks,timing,questionType) = self.questionQueue.popleft()

            # Starts the question timer
            self.startQuestionTimerSP(timing)

        # Allows variables to be accessed
            self.currentImagePath = QtGui.QPixmap(imagePath)
            self.currentMarkSchemePath = QtGui.QPixmap(markschemePath)
            self.currentCorrectAnswer = correctAnswer
            self.currentMarks = marks
            self.currentQuestionType = questionType
                    
        # Displays question
            self.ui.mainS.setPixmap(self.currentImagePath)

        # Resets the progress bar
            self.progressBar = 0

        # For each bot their statistics are updated
            for i in range(0,3):
                # Returns an array of the bot's time taken and answer status
                botStatus = self.botTimeTaken(i)

                # Seperates time taken and answer status
                botTime = botStatus[0]
                isCorrect = botStatus[1]

                # Changes the dictionary to the new statistics
                self.bots[i]["timing"] = botTime
                self.bots[i]["isCorrect"] = isCorrect

        # Starts the timer until the bot submit their answer
            self.startBotTimer(0,self.bots[0]["timing"])
            self.startBotTimer(1,self.bots[1]["timing"])
            self.startBotTimer(2,self.bots[2]["timing"])

        # Resets bot's profile picture
            self.botPicture()

    


    # Once the match is finished this is executed
    def endRoundSP(self):
        # Finds the user ID and displays the name of the user
        userid = self.sessions[self.token]["userid"]
        username = fetchUserName(userid)

        # Sets the name of the players
        self.ui.player1TextSingle.setText(username)
        self.ui.stackedWidget.setCurrentIndex(12)
        # Sets the points of the player
        self.ui.player1TextSingle_24.setText(str(self.matchPoints))

        # Sets the name and points of bot 1
        self.ui.player2TextSingle.setText(self.bots[0]["name"])
        self.ui.player1TextSingle_25.setText(str(self.bots[0]["points"]))

        # Sets the name and points of bot 2
        self.ui.player3TextSingle.setText(self.bots[1]["name"])
        self.ui.player1TextSingle_47.setText(str(self.bots[1]["points"]))

        # Sets the name and points of bot 3
        self.ui.player4TextSingle.setText(self.bots[2]["name"])
        self.ui.player1TextSingle_53.setText(str(self.bots[2]["points"]))

        # Hides status label (for future updates when adding 5 question game modes)
        self.ui.player1TextSingle_5.hide()
        self.ui.player1TextSingle_10.hide()
        self.ui.player1TextSingle_6.hide()
        self.ui.player1TextSingle_11.hide()
        self.ui.player1TextSingle_19.hide()
        self.ui.player1TextSingle_18.hide()
        self.ui.player1TextSingle_14.hide()
        self.ui.player1TextSingle_48.hide()
        self.ui.player1TextSingle_49.hide()
        self.ui.player1TextSingle_46.hide()
        self.ui.player1TextSingle_42.hide()
        self.ui.player1TextSingle_62.hide()
        self.ui.player1TextSingle_54.hide()
        self.ui.player1TextSingle_63.hide()
        self.ui.player1TextSingle_57.hide()
        self.ui.player1TextSingle_20.hide()

        # Displays questions which the players have gotten correct

        # Player question history
        self.ui.player1TextSingle_2.setText(self.userCorrect[0])
        self.ui.player1TextSingle_3.setText(self.userCorrect[1])
        self.ui.player1TextSingle_4.setText(self.userCorrect[2])

        # Bot 1 question history
        self.ui.player1TextSingle_15.setText(self.bot1Correct[0])
        self.ui.player1TextSingle_16.setText(self.bot1Correct[1])
        self.ui.player1TextSingle_21.setText(self.bot1Correct[2])

        # Bot 2 question history
        self.ui.player1TextSingle_43.setText(self.bot2Correct[0])
        self.ui.player1TextSingle_44.setText(self.bot2Correct[1])
        self.ui.player1TextSingle_50.setText(self.bot2Correct[2])

        # Bot 3 question history
        self.ui.player1TextSingle_59.setText(self.bot3Correct[0])
        self.ui.player1TextSingle_60.setText(self.bot3Correct[1])
        self.ui.player1TextSingle_61.setText(self.bot3Correct[2])

        # Changes profile pictures of players (final page)

        # Sets the icon of the 1st bot
        icon1 = QtGui.QPixmap(self.bots[0]["profilePicture"])
        self.ui.player2TextSingle.setStyleSheet(f"color: white;")
        self.ui.player2IconSingle.setPixmap(icon1)

        # Sets the icon of the 2nd bot
        icon2 = QtGui.QPixmap(self.bots[1]["profilePicture"])
        self.ui.player3TextSingle.setStyleSheet(f"color: white;")
        self.ui.player3IconSingle.setPixmap(icon2)

        # Sets the icon of the 3rd bot
        icon3 = QtGui.QPixmap(self.bots[2]["profilePicture"])
        self.ui.player4TextSingle.setStyleSheet(f"color: white;")
        self.ui.player4IconSingle.setPixmap(icon3)

        # Checks to see who won
        pointsComparer = []

        # Adds the scores of the bots
        for index in range(0,3):

            pointsComparer.append({
                                "name": self.bots[index]["name"],
                                "points": self.bots[index]["points"]
                            })   
            
        # Adds the score of the player
        pointsComparer.append({
            "name": username,
            "points": self.matchPoints
        })

        # Sorts the list
        pointsComparer.sort(key = lambda most: most["points"], reverse = True)

        # Adds the name of the winner
        self.ui.player1TextSingle_64.setText(pointsComparer[0]["name"])

        # Awards points for performance
        points = [25,15,5,0]

        # Tracks the previous' player score and their position in the rankings
        lastScore = -1
        previousPlayerPosition = -1

        # Searches through array
        for index in range(len(pointsComparer)):

            # If the player score is not equal to the last score then a new last score is set

            if pointsComparer[index]["points"] != lastScore:

                # Previous index stored in case user is in same position (same points awarded)
                previousPlayerPosition = index

                # Previous score stored to compare with next score 
                lastScore = pointsComparer[index]["points"]

            # Adds points (Only for player)
            if pointsComparer[index]["name"] == username:
                addPoints(userid,points[previousPlayerPosition])

            # Updates all the points label
            self.pointsUpdater(userid)
                
    # Used to set the cosmetics equipped (For singleplayer mode)
    def setCosmetics(self, userid):
        # Finds the users equipped item
        item = findEquippedItem(userid)
        
        # If the equipped item variable is not empty
        if item is not None:

            # If the item id lies between 0 or 5 inclusive
            if item >= 0 and item < 6:
                
                # Maps the id to a specific colour (points module shows this mapping)
                colourMap = {
                        0: "blue",
                        1: "red",
                        2: "yellow",
                        3: "green",
                        4: "pink",
                        5: "purple"
                    }
                
                # Gets the item based on the provided item id 
                colour = colourMap.get(item,"white")
                # Changes the label colour
                self.ui.player1TextSingle.setStyleSheet(f"color: {colour};")
                self.ui.connectingPlayerText.setStyleSheet(f"color: {colour};")

                # Changes the icon to the default profile
                self.ui.player1IconSingle.setPixmap(QtGui.QPixmap("icons/default.png"))
                self.ui.label_9.setPixmap(QtGui.QPixmap("icons/default.png"))
            
            # If the item id is greater than 5
            elif item > 5:
                iconMap = {
                    6: "icons/MaleMathematician.png",
                    7: "icons/FemaleMathematician.png",
                    8: "icons/Physics.png",
                    9: "icons/Chemistry.png",
                    10: "icons/Biology.png",
                    11: "icons/Einstein.png",
                    12: "icons/Cringeman.png",
                    13: "icons/GreekAlphabet.png",
                    14: "icons/GoldenFish.png"
                    }
                
                self.ui.player1IconSingle.setPixmap(QtGui.QPixmap(iconMap.get(item)))
                self.ui.label_9.setPixmap(QtGui.QPixmap(iconMap.get(item)))
                self.ui.connectingPlayerIcon.setPixmap(QtGui.QPixmap(iconMap.get(item)))
        else:
            self.ui.player1TextSingle.setStyleSheet(f"color: white;")
            self.ui.player1IconSingle.setPixmap(QtGui.QPixmap(f"color: white;"))
            self.ui.player1IconSingle.setPixmap(QtGui.QPixmap("icons/default.png"))
            self.ui.connectingPlayerIcon.setPixmap(QtGui.QPixmap("icons/default.png"))
            self.ui.label_9.setPixmap(QtGui.QPixmap("icons/default.png"))
    


    # Adds the bots the user will play with
    def addBot(self, botid):

        # Chooses a random name
        names = ["Christopher","Tyler","Curtis","Samantha","Tommy","Emma","Cindy","Ruth"]

        # Chooses a random personalities
        playerType = ["newbie","regular","clutch","pro"]
        chosenPlayerType = random.choice(playerType)

        # Changes the profile picture based on the player type
        if chosenPlayerType == "newbie":
            profilePicture = "icons/Newbie.png"
        elif chosenPlayerType == "regular":
            profilePicture = "icons/Regular.png"
        elif chosenPlayerType == "clutch":
            profilePicture = "icons/clutch.png"
        else:
            profilePicture = "icons/Pro.png"


        # Chooses a random time when the bot completes the question
        botStatus = self.botTimeTaken(chosenPlayerType)
        time = botStatus[0]
        isCorrect = botStatus[1]
        
        # Adds the bot into the bots dictionary 
        self.bots[botid] = {
            "name": random.choice(names),
            "playerType": chosenPlayerType,
            "timing": time,
            "isCorrect": isCorrect,
            "points": 0,
            "profilePicture": profilePicture,
        }

    # Stops all the bots Timer
    def stopBotTimer(self):
        self.bot1Timer.stop()
        self.bot2Timer.stop()
        self.bot3Timer.stop()



    # Generates a random time taken which the bot will take to finish the question
    def botTimeTaken(self,playerType):
        
        # Possible answer status
        answerStatusOptions = ["Correct","Incorrect"]

        # Newbies take the longest to finish (self.bots[botid][1] finds the personality in the bots array)
        if playerType == "newbie":

            # Generates a random time taken
            lowerlimit = int(self.maxTiming * 0.85)
            timeTaken = random.randint(lowerlimit, self.maxTiming)
            # Generates an answer status (50% chance of correct answer)
            answerStatus = random.choices(answerStatusOptions, weights=[0.5,0.5],k=1)[0]
            return timeTaken, answerStatus
        
        # Regular take a normal time to finish
        elif playerType == "regular":
            
            # Generates a random time taken
            lowerlimit = int(self.maxTiming * 0.75)
            timeTaken = random.randint(lowerlimit, int(self.maxTiming * 0.9))
            
            # Generates an answer status (70% chance of correct answer)
            answerStatus = random.choices(answerStatusOptions, weights=[0.7, 0.3],k=1)[0]
            return timeTaken, answerStatus
        
        # Clutch play like regular but get harder as the rounds progress.
        elif playerType == "clutch":

            # Play like regular player
            if self.rounds > 1:
                lowerlimit =int(self.maxTiming * 0.4)
                timeTaken = random.randint(lowerlimit,int(self.maxTiming * 0.8))

                answerStatus = random.choices(answerStatusOptions, weights=[0.7, 0.3],k=1)[0]
                return timeTaken, answerStatus
            # if last round then upgrade difficulty
            else:
                lowerlimit = int(self.maxTiming * 0.75)
                timeTaken = random.randint(lowerlimit, int(self.maxTiming * 0.9))

            # Generates an answer status (90% chance of correct answer)
                answerStatus = random.choices(answerStatusOptions, weights=[0.9, 0.1],k=1)[0]
                return timeTaken, answerStatus
            
        # Pro is the best players (completes question in quickest time)
        else:
            lowerlimit = int(self.maxTiming * 0.4) 
            timeTaken = random.randint (lowerlimit,int(self.maxTiming * 0.6))

            # Generates an answer status (95% chance of correct answer)
            answerStatus = random.choices(answerStatusOptions, weights=[0.95, 0.05],k=1)[0]
            return timeTaken, answerStatus


    # Starts the bot timer 
    def startBotTimer(self, botid, time):

        # Bot IDs are matched to a timer (these timers are important so they can be ended at the end of a round)
        match botid:
            case 0:
                self.bot1Timer = QtCore.QTimer(self)
                
                # Assigns a function once the timer is stopped
                self.bot1Timer.timeout.connect(lambda: self.botFinished(botid))
                self.bot1Timer.start(time * 1000)

            case 1:
                self.bot2Timer = QtCore.QTimer(self)

                # Assigns a function once the timer is stopped
                self.bot2Timer.timeout.connect(lambda: self.botFinished(botid))
                self.bot2Timer.start(time * 1000)

            case 2:
                self.bot3Timer = QtCore.QTimer(self)

                # Assigns a function once the timer is stopped
                self.bot3Timer.timeout.connect(lambda: self.botFinished(botid))
                self.bot3Timer.start(time * 1000)
        

    # Changes profile picture of bots once finished a question
    def botFinished(self,botid):
        # Updates the bots profile picture once they have completed a question
        if botid == 0:
             icon = QtGui.QPixmap("icons/CompletedQuestion.png")
             self.ui.label_8.setPixmap(icon)
             self.bot1Timer.stop()
        elif botid == 1:
            icon = QtGui.QPixmap("icons/CompletedQuestion.png")
            self.ui.label_7.setPixmap(icon)
            self.bot2Timer.stop()
        elif botid == 2:
            icon = QtGui.QPixmap("icons/CompletedQuestion.png")
            self.ui.label_6.setPixmap(icon)
            self.bot3Timer.stop()



    # Changes profile picture of bots to their class
    def botPicture(self):

        # Sets the icon of the first player
        icon1 = QtGui.QPixmap(self.bots[0]["profilePicture"])
        self.ui.label_8.setPixmap(icon1)

        # Sets the icon of the second player
        icon2 = QtGui.QPixmap(self.bots[1]["profilePicture"])
        self.ui.label_7.setPixmap(icon2)

        # Sets the icon of the third player
        icon3 = QtGui.QPixmap(self.bots[2]["profilePicture"])
        self.ui.label_6.setPixmap(icon3)
        # Note: these icons represent the bots difficulty level.

    ## END OF SINGLEPLAYER LOGIC

    ## START OF MULTIPLAYER LOGIC

    # Selects the multiplayer mode and navigates to host page
    def selectMultiPlayer(self):
        self.selectedMode = "multiplayer"
        self.ui.stackedWidget.setCurrentIndex(5)



    # Hosts a game 
    def hostGame(self, year):

        self.isServer = True

        # Selected multiplayer year
        self.multiplayerYear = year
        # Switches to connection page
        self.ui.stackedWidget.setCurrentIndex(2)

        # Fetches user id from the token
        userid = self.sessions[self.token]["userid"]
        
        # Fetches name and equipped item
        name = fetchUserName(userid)
        equippedItem = findEquippedItem(userid)

        # Enters the hosts details into connected players
        updateDetails(name,equippedItem)

        # Begins the server
        startServer() 

        # Creates a seperate thread (Prevents blocking the ui with infinite loops)
        threading.Thread(
            # Function to be concurrently executed
            target = acceptClients, 
            # Thread closes after server exits
            daemon= True 
        ).start()

        # Timer to regularly check players connected every second
        self.playerCheckTimer = QtCore.QTimer(self) 
        self.playerCheckTimer.timeout.connect(self.checkPlayers)
        self.playerCheckTimer.start(1000)
        userid = self.sessions[self.token]["userid"]
        self.setCosmetics(userid)

    def clientAcceptHandler(self):
        try:
            acceptClients
        finally:


            # Reset timers
            self.ui.stackedWidget.setCurrentIndex(0)            

            

    # Function repeatedly called every second
    def checkPlayers(self):

        # Checks if the number of players in the server is > 0
        if len(server.connectedPlayers) > 1:
                
                # Array of player names and adds player names to list
                playerNames = []
                for index in range(0, len(server.connectedPlayers)):
                    playerNames.append(server.connectedPlayers[index]["name"])

                # Alerts host of player connected
                self.ui.connectingText.setText(f"{len(server.connectedPlayers)} Players connected")
                confirmed = self.playConfirmationPopup(f"Current Players: {playerNames} \n Would you like to start?")

                # If host clicks yes then start game
                if confirmed:
                    self.startMultiplayerGameHost()
                    self.playerCheckTimer.stop()
        else:
            # Sets text to connecting if no one is online
            self.ui.connectingText.setText("Connecting")
        


    # Starts the game as a host
    def startMultiplayerGameHost(self):
        
        # Retrieves question from provided year
        questions = questionRetrieval(self.multiplayerYear) 

        # Array for storing question ids distributed to other devices
        questionids = []

        # Adds each question id into a list (in order)
        for question in questions:
            questionids.append(question[0])

        self.isServer = True

        # Sends a message to all the clients that game is starting
        startGame(questionids)
        
        # Sets the last score of the player
        self.lastScore = 0

        # Sets the number of rounds
        self.rounds = 3

        # Makes a queue and adds all questions to that queue
        self.questionQueue = deque()

        for q in questions:
            self.questionQueue.append(q)

        # Removes first item in queue and assigns temporary variables
        (questionID,year,imagePath,markschemePath,correctAnswer,marks,timing,questionType) = self.questionQueue.popleft()

        # Total points obtained during a match
        self.matchPoints = 0

        # Allows variables to be accessed
        self.currentImagePath = QtGui.QPixmap(imagePath)
        self.currentMarkSchemePath = QtGui.QPixmap(markschemePath)
        self.currentCorrectAnswer = correctAnswer
        self.currentMarks = marks
        self.currentQuestionType = questionType
        self.maxTiming = timing

        # Displays question
        self.ui.mainM.setPixmap(self.currentImagePath)

        # Progress bar setup
        self.progressBar = 0

        # Cycles through all connected players and updates the pictures based on their stats
        for index, player in enumerate(server.connectedPlayers.values()):
            self.setCosmeticsMultiPlayer(player["equippedItem"], index)

        # Switches to main game
        self.ui.stackedWidget.setCurrentIndex(13)

        QtCore.QTimer.singleShot(500,self.playerStatusProfilePictures)

        self.startQuestionTimerMP(self.maxTiming)
        
        self.clientCheckTimer = QtCore.QTimer(self)
        self.clientCheckTimer.timeout.connect(self.clientCheckHandler)
        # Checks every 0.2 seconds
        self.clientCheckTimer.start(200) 

    # Client choosing to join the game
    def joinGame(self):

        self.isClient = True

        # Fetches user id from the token
        userid = self.sessions[self.token]["userid"]
        
        # Fetches name and equipped item
        name = fetchUserName(userid)
        equippedItem = findEquippedItem(userid)

        target = self.joinHandler(name,equippedItem), 


    # Check if server is available and displays appropriate information
    def joinHandler(self,name,equippedItem):
        isConnected = connect(name,equippedItem)

        if isConnected == False:
            self.warningPopup("No Servers Found")
            self.ui.stackedWidget.setCurrentIndex(0)
        else:
            # Changes page to connecting page
            self.ui.stackedWidget.setCurrentIndex(2)



            self.serverCheckTimer = QtCore.QTimer(self)
            self.serverCheckTimer.timeout.connect(self.serverCheckHandler)
            # Checks every 0.2 seconds
            self.serverCheckTimer.start(200) 

            # Starts a timer which updates frequently to check the game status (check if host is ready)
            self.gameLoadingTimer = QtCore.QTimer(self)
            self.gameLoadingTimer.timeout.connect(self.checkGameRunning)
            self.gameLoadingTimer.start(1000)

    # FOR SERVER: Checks if any of the clients have disconnected
    def clientCheckHandler(self):
        if checkClients():
            self.clientCheckTimer.stop()

            try:
                self.questionTimer.stop()
            except:
                pass

            self.isServer = False
            self.warningPopup("Client has left the game.")
            self.ui.stackedWidget.setCurrentIndex(0)    

     # FOR CLIENT: Checks if the server is still available
    def serverCheckHandler(self):

        serverStatus = checkServer()

        reject = serverStatus[0]

        if reject:
            
            reasonForRejection = serverStatus[1]
            self.serverCheckTimer.stop()

            try:
                self.questionTimer.stop()
            except:
                pass

            self.isClient = False

            if reasonForRejection == "left":
                self.warningPopup("Host has left the game.")
                self.ui.stackedWidget.setCurrentIndex(0) 

            elif reasonForRejection == "full":
                self.warningPopup("Server Full.")
                self.ui.stackedWidget.setCurrentIndex(0) 

            else:
                self.warningPopup("Round In Session Please Wait For Round To Finish.")
                self.ui.stackedWidget.setCurrentIndex(0) 


    # Checks if a game is in session 
    def checkGameRunning(self):
        if clientModule.gameStart:
            self.startMultiplayerGameClient()
            self.gameLoadingTimer.stop()

    # Function that quits a connecting sequence when trying to connect to the server or hosting a game
    def leaveConnecting(self):

        if self.isClient:
            endConnectionClient()
        else:
            endConnectionServer()

        self.isClient = False
        self.isServer = False
        self.ui.stackedWidget.setCurrentIndex(0) 


    # Starts the multiplayer game as a client
    def startMultiplayerGameClient(self):

        # Fetchs question ids from host
        self.questionids = fetchQuestionidsFromServer()
        self.questions = []
        
        # Adds questions to a list 
        for questionid in self.questionids:
            self.questions.append(questionRetrievalID(questionid))

        # Sets the last score of the player
        self.lastScore = 0

        # Sets the number of rounds
        self.rounds = 3

        self.isClient = True

        # Makes a queue and adds all questions to that queue
        self.questionQueue = deque()

        # Appends questions into a queue
        for q in self.questions:
            self.questionQueue.append(q)

        # Removes first item in queue and assigns temporary variables
        (questionID,year,imagePath,markschemePath,correctAnswer,marks,timing,questionType) = self.questionQueue.popleft()

        # Total points obtained during a match
        self.matchPoints = 0

        # Allows variables to be accessed
        self.currentImagePath = QtGui.QPixmap(imagePath)
        self.currentMarkSchemePath = QtGui.QPixmap(markschemePath)
        self.currentCorrectAnswer = correctAnswer
        self.currentMarks = marks
        self.currentQuestionType = questionType
        self.maxTiming = timing

        # Displays question
        self.ui.mainM.setPixmap(self.currentImagePath)

        # Progress bar setup
        self.progressBar = 0

        # Cycles through connected players and updates profile pictures
        for index, player in enumerate(clientModule.connectedPlayers.values()):
            self.setCosmeticsMultiPlayer(player["equippedItem"], index)

        # Switches to main game
        self.ui.stackedWidget.setCurrentIndex(13)
        
        QtCore.QTimer.singleShot(500,self.playerStatusProfilePictures)

        self.startQuestionTimerMP(self.maxTiming)


    # Sets cosmetics for players
    def setCosmeticsMultiPlayer(self,equippedItem,id):

        # Maps the specific player id with profile pictures and labels
        mainGameProfilePictures = {
            0: self.ui.multiPlayer1,
            1: self.ui.multiPlayer2,
            2: self.ui.multiPlayer3,
            3: self.ui.multiPlayer4
        }
        endPageProfilePictures = { 
            0: self.ui.player1IconSingle,
            1: self.ui.player2IconSingle,
            2: self.ui.player3IconSingle,
            3: self.ui.player4IconSingle
        }
        endPageNameTags = {
            0: self.ui.player1TextSingle,
            1: self.ui.player2TextSingle,
            2: self.ui.player3TextSingle,
            3: self.ui.player4TextSingle
        }

        # Checks if equipped item is not empty
        if equippedItem is not None:

            # Checks if equipped item id is between 0 and 5 inclusive
   
            if equippedItem >= 0 and equippedItem < 6:
                colourMap = {
                        0: "blue",
                        1: "red",
                        2: "yellow",
                        3: "green",
                        4: "pink",
                        5: "purple"
                    }
                # Fetches colour from colour map
                colour = colourMap.get(equippedItem,"white")

                # Assigns colour of nametag of player
                endPageNameTags[id].setStyleSheet(f"color: {colour};")

                # Changes the profile picture to default profile
                mainGameProfilePictures[id].setPixmap(QtGui.QPixmap("icons/default.png"))
                endPageProfilePictures[id].setPixmap(QtGui.QPixmap("icons/default.png"))

            # Checks if equipped item is greater than 5
            elif equippedItem > 5:
                iconMap = {
                    6: "icons/MaleMathematician.png",
                    7: "icons/FemaleMathematician.png",
                    8: "icons/Physics.png",
                    9: "icons/Chemistry.png",
                    10: "icons/Biology.png",
                    11: "icons/Einstein.png",
                    12: "icons/Cringeman.png",
                    13: "icons/GreekAlphabet.png",
                    14: "icons/GoldenFish.png"
                    }
                
                # Changes profile pictures
                mainGameProfilePictures[id].setPixmap(QtGui.QPixmap(iconMap.get(equippedItem)))
                endPageProfilePictures[id].setPixmap(QtGui.QPixmap(iconMap.get(equippedItem)))
        else:
            # Changes everything to default if equipped item is none
            endPageNameTags[id].setStyleSheet(f"color: white;")
            mainGameProfilePictures[id].setPixmap(QtGui.QPixmap("icons/default.png"))
            endPageProfilePictures[id].setPixmap(QtGui.QPixmap("icons/default.png"))
            
        # Begins the question timer
    def startQuestionTimerMP(self, time):

        # Sets the maximum timer count and the timer
        self.questionTimerCount = time
        self.questionTimer = QtCore.QTimer(self)

        # Assigns a function once the timer is stopped
        self.questionTimer.timeout.connect(self.updateQuestionTimerMP)

        # Updates timer every 1 second
        self.questionTimer.start(1000)



    # Updates the labels and timer every second
    def updateQuestionTimerMP(self):

        # Minute and seconds display
        minutes = self.questionTimerCount //  60
        seconds = self.questionTimerCount % 60

        if seconds <= 9:
            self.ui.multiTimer.setText(f"{minutes}:0{seconds}")   
        else:
            self.ui.multiTimer.setText(f"{minutes}:{seconds}")   

        #Decrements timer
        self.questionTimerCount -= 1
        
        #Increments progressBar
        self.progressBar += 100/(self.maxTiming)

        # Sometimes the bar exeeds 100 percent due to rounding
        if self.progressBar > 100:
            self.progressBar = 100

        # Sets value of test progress
        self.ui.multiProgress.setValue(int(self.progressBar))

        # Stops timer if time runs out
        if self.questionTimerCount < 0:
            self.timeUpMP()

    # Changes profile picture of the players 
    def playerFinished(self,id):
        
        mainGameProfilePictures = {
            0: self.ui.multiPlayer1,
            1: self.ui.multiPlayer2,
            2: self.ui.multiPlayer3,
            3: self.ui.multiPlayer4
        }

        icon = QtGui.QPixmap("icons/CompletedQuestion.png")
        mainGameProfilePictures[id].setPixmap(icon)

    # Changes the profile picture when a player has submitted
    def playerStatusProfilePictures(self):

        # If player is client
        if self.isClient:

            # Fetches submitted players from client module
            submittedPlayers = checkSubmittedPlayersClient()

            # Cycles through submitted players and changes profile pictures
            if submittedPlayers:
                for player in submittedPlayers:
                    self.playerFinished(player)

        # If player is server
        elif self.isServer:
            # Checks submitted players from server module
            submittedPlayers = checkSubmittedPlayersServer()

            # Cycles through submitted players and changes profile pictures
            if submittedPlayers:
                for player in submittedPlayers:
                    self.playerFinished(player)

        # Resets timer which changes profile pictures again after 500 ms
        QtCore.QTimer.singleShot(500,self.playerStatusProfilePictures)

                

    # If player submits their answer
    def submitAnswerMP(self):

        self.completionTime = self.maxTiming - self.questionTimerCount

        # Checks if player is client
        if self.isClient:
            # Alerts server that client has submitted answer
            tellServerSubmitAnswer()
            # Starts timer to check if round is finished
            QtCore.QTimer.singleShot(500,self.checkRoundFinishedClient)

        # Checks if player is server
        else:
            # Adds servers answer to submitted players array
            submitAnswerServer()

            # Starts a timer which checks regularly if players have submitted
            QtCore.QTimer.singleShot(500,self.checkRoundFinishedServer)
        
        # Hides Submit and input 
        self.ui.inputM.hide()
        self.ui.submitMulti.hide()
        self.ui.multiBottomLine1.hide()
        self.ui.multiBottomLine2.hide()

    # Checks if round is finished (all clients have submitted)
    def checkRoundFinishedServer(self):  
        data = checkAllPlayerSubmit()
        
        # Checks if everyone submitted
        if data == "End Round":
            self.timeUpMP()
            resetSubmittedPlayersServer()

        elif data == "Continue":
            # Sets a timer that regularly checks if players have submitted
            QtCore.QTimer.singleShot(500,self.checkRoundFinishedServer)

    def checkRoundFinishedClient(self):
        data = roundInProgress()
        if data == "Continue":
            QtCore.QTimer.singleShot(500,self.checkRoundFinishedClient)
        elif data == "End Round":
            self.timeUpMP()
            resetSubmittedPlayersClient()


    # Function executed when time is expired
    def timeUpMP(self):

        # Stops the timer 
        self.questionTimer.stop()

        # Decrements the number of rounds
        self.rounds -= 1

        # Goes to mark scheme page
        self.ui.stackedWidget.setCurrentIndex(4)

        # Shows the mark scheme
        self.ui.markSchemeImage.setPixmap(self.currentMarkSchemePath)

        # Converts user answer to text
        userAnswer = self.ui.inputM.toPlainText()
        self.ui.userAnswerLabel.setText(userAnswer)


        # Checks to see if the user answers are correct
        if mathAnswerChecker(userAnswer,self.currentCorrectAnswer,self.currentQuestionType):
            self.isCorrect = "Correct"
            if self.isServer:

                self.matchPoints = retrievePlayerScoreServer()

            elif self.isClient:
                self.matchPoints = retrievePlayerScoreClient()

            if self.matchPoints == False:
                self.matchPoints = 0
            

            # Awards full marks 
            self.matchPoints += self.currentMarks
        else:
            self.isCorrect= "Incorrect"
        
        # If server Checks if all clients has sent data 
        if self.isServer:
                QtCore.QTimer.singleShot(300,self.checkIfClientsDataSent)

        # Sends data to server
        elif self.isClient:
            updateStats(self.isCorrect, self.completionTime, self.matchPoints)
            QtCore.QTimer.singleShot(300,self.checkIfOthersSubmit)
    
    # Displays stats end of round
    def displayStats(self):

        # If server
        if self.isServer:

             # Retrieves all other players statistics
            connectedPlayers = retrievePlayersServer()

            # Checks user score
            score = retrievePlayerScoreServer()

            # Checks if answer is correct
            isCorrect = isPlayerCorrectServer()
            
            pointsGained = score - self.lastScore

            # Checks if the user has got it correct
            if isCorrect == "Correct":
                bonus = pointsGained - self.currentMarks
            else: 
                bonus = 0

            # Assigns the text
            text = f"You have gained {pointsGained} Points\n" 
            text += f"Total points: {score}\n"
            text += f"Bonus: {bonus}\n"

            # Sets the last score and the score of this round
            self.lastScore = score

            # For loop adding player names (connectedPlayers array does not contain the player themself only other players)
            for player in connectedPlayers.values():
                text += f"{player['name']}: {player['points']} Points\n"
                text += f"Answer: {player['isCorrect']} completed in "
                text += f"{player['timing'] // 60} minutes and {player['timing'] % 60} seconds\n"
            self.ui.userPointsLabel.setText(text)

        elif self.isClient:
            # Retrieves all other players statistics
            connectedPlayers = retrievePlayersClient()

            # Checks user score
            score = retrievePlayerScoreClient()

            # Checks if answer is correct
            isCorrect = isPlayerCorrectClient()

            pointsGained = score - self.lastScore

            # Checks if the user has got it correct
            if isCorrect == "Correct":
                bonus = pointsGained - self.currentMarks
            else: 
                bonus = 0

            # Assigns the text
            text = f"You have gained {pointsGained} Points\n" 
            text += f"Total points: {score}\n"
            text += f"Bonus: {bonus} \n"

            # Sets the last score and the score of this round
            self.lastScore = score

            # Iterates through list containing stats of other players and displays their stats
            for player in connectedPlayers.values():

                text += f"{player['name']}: {player['points']} Points\n"
                text += f"Answer: {player['isCorrect']} completed in "
                text += f"{player['timing'] // 60} minutes and {player['timing'] % 60} seconds\n"

            self.ui.userPointsLabel.setText(text)
                # Goes to mark scheme page
        self.ui.stackedWidget.setCurrentIndex(4)

         

                
    # Checks if the clients have all sent their status
    def checkIfClientsDataSent(self):

        # If they have then update time and calculate points
        if dataSentCheckerServer():
            updateTime(self.isCorrect, self.completionTime, self.matchPoints)
            pointsCalculator()
            self.displayStats()
            QtCore.QTimer.singleShot(20000,self.intermissionTimerMP)

        else:
            QtCore.QTimer.singleShot(300,self.checkIfClientsDataSent)



    # Updates stats and check if all player have submitted (client)
    def checkIfOthersSubmit(self):

        # Checks if all players have submitted
        if dataSentCheckerClient():
            self.displayStats()
            QtCore.QTimer.singleShot(20000,self.intermissionTimerMP)

        else: 
            # Otherwise another check every 300ms is carried out
            QtCore.QTimer.singleShot(300,self.checkIfOthersSubmit)

    # Time before next round begins
    def intermissionTimerMP(self):

        # Checks if all rounds are over
        if self.rounds == 0:
            self.endRoundMP()
        # Move to next round
        else:
            self.nextRoundMP()
        
    # Starts the next round
    def nextRoundMP(self):
        
        clientModule.round = True

        # Shows the submit button and Qedit Label
        self.ui.submitMulti.show()
        self.ui.inputM.show()
        self.ui.multiBottomLine1.show()
        self.ui.multiBottomLine2.show()

        # Removes first item in queue and assigns temporary variables
        (questionID,year,imagePath,markschemePath,correctAnswer,marks,timing,questionType) = self.questionQueue.popleft()

        # Allows variables to be accessed
        self.currentImagePath = QtGui.QPixmap(imagePath)
        self.currentMarkSchemePath = QtGui.QPixmap(markschemePath)
        self.currentCorrectAnswer = correctAnswer
        self.currentMarks = marks
        self.currentQuestionType = questionType
        self.maxTiming = timing

        # Displays question
        self.ui.mainM.setPixmap(self.currentImagePath)

        # Progress bar setup
        self.progressBar = 0


        if self.isClient:
            # Cycles through connected players and updates profile pictures based on their stats
            for index, player in enumerate(clientModule.connectedPlayers.values()):
                self.setCosmeticsMultiPlayer(player["equippedItem"], index)

        else:
            # Cycles through all connected players and updates the pictures based on their stats
            for index, player in enumerate(server.connectedPlayers.values()):
                self.setCosmeticsMultiPlayer(player["equippedItem"], index)

        # Switches to main game
        self.ui.stackedWidget.setCurrentIndex(13)
        
        # Starts a timer which regularly updates the players profile pictures
        QtCore.QTimer.singleShot(500,self.playerStatusProfilePictures)

        self.startQuestionTimerMP(self.maxTiming)

    # Function run when round ends.
    def endRoundMP(self):
        
        # Finds the user ID and displays the name of the user
        userid = self.sessions[self.token]["userid"]

        pointLabelMap = {
            0: self.ui.player1TextSingle_24,
            1: self.ui.player1TextSingle_25,
            2: self.ui.player1TextSingle_47,
            3: self.ui.player1TextSingle_53
        }
        textLabelMap = {
            0: self.ui.player1TextSingle,
            1: self.ui.player2TextSingle,
            2: self.ui.player3TextSingle,
            3: self.ui.player4TextSingle
        }

        if self.isClient:
            connectedPlayers = clientModule.connectedPlayers

            for key, value in connectedPlayers.items():
                id = int(key)
                pointLabelMap[id].setText(str(value["points"]))
                textLabelMap[id].setText(str(value["name"]))
            
        elif self.isServer:
            connectedPlayers = server.connectedPlayers

            for key, value in connectedPlayers.items():
                id = int(key)
                pointLabelMap[id].setText(str(value["points"]))
                textLabelMap[id].setText(str(value["name"]))

        self.ui.stackedWidget.setCurrentIndex(12)

        if len(connectedPlayers) == 2:
            # Hides displays intended for 4 players
            self.ui.player1TextSingle_40.hide()
            self.ui.player1TextSingle_41.hide()
            self.ui.player1TextSingle_45.hide()
            self.ui.player1TextSingle_43.hide()
            self.ui.player1TextSingle_44.hide()
            self.ui.player1TextSingle_50.hide()
            self.ui.player1TextSingle_47.hide()
            self.ui.player1TextSingle_51.hide()

            self.ui.player3TextSingle.hide()
            self.ui.player3IconSingle.hide()

            self.ui.player1TextSingle_55.hide()
            self.ui.player1TextSingle_59.hide()
            self.ui.player1TextSingle_58.hide()
            self.ui.player1TextSingle_53.hide()
            self.ui.player1TextSingle_60.hide()
            self.ui.player1TextSingle_56.hide()
            self.ui.player1TextSingle_61.hide()
            self.ui.player1TextSingle_52.hide()
            
            self.ui.player4IconSingle.hide()
            self.ui.player4TextSingle.hide()

            possibleScores = [35, 5]

        elif len(connectedPlayers) == 3:
            # Hides displays intended for 4 players
            self.ui.player1TextSingle_55.hide()
            self.ui.player1TextSingle_59.hide()
            self.ui.player1TextSingle_58.hide()
            self.ui.player1TextSingle_53.hide()
            self.ui.player1TextSingle_60.hide()
            self.ui.player1TextSingle_56.hide()
            self.ui.player1TextSingle_61.hide()
            self.ui.player1TextSingle_52.hide()
            self.ui.player4IconSingle.hide()
            self.ui.player4TextSingle.hide()
            possibleScores = [35,15,5]

        else:
            possibleScores = [35,25,15,5]

        self.ui.player1TextSingle_5.hide()
        self.ui.player1TextSingle_10.hide()
        self.ui.player1TextSingle_6.hide()
        self.ui.player1TextSingle_11.hide()
        self.ui.player1TextSingle_19.hide()
        self.ui.player1TextSingle_18.hide()
        self.ui.player1TextSingle_14.hide()
        self.ui.player1TextSingle_48.hide()
        self.ui.player1TextSingle_49.hide()
        self.ui.player1TextSingle_46.hide()
        self.ui.player1TextSingle_42.hide()
        self.ui.player1TextSingle_62.hide()
        self.ui.player1TextSingle_54.hide()
        self.ui.player1TextSingle_63.hide()
        self.ui.player1TextSingle_57.hide()
        self.ui.player1TextSingle_20.hide()

        # Checks to see who won
        pointsComparer = []

        # Adds the scores of the bots
        for key, value in connectedPlayers.items():

            pointsComparer.append({
                                "name": value["name"],
                                "points": value["points"],
                                "ID": key
                            })   

        # Sorts the list
        pointsComparer.sort(key = lambda most: most["points"], reverse = True)

        # Adds the name of the winner
        self.ui.player1TextSingle_64.setText(pointsComparer[0]["name"])
        lastScore = -1
        previousPlayerPosition = -1

        if self.isClient:
            playerid = retrievePlayerID()
        else:
            playerid = 0
            
        for index, values in enumerate(pointsComparer):

            # If the player score is not equal to the last score then a new last score is set
            if values["points"] != lastScore:

                # Previous index stored in case user is in same position (same points awarded)
                previousPlayerPosition = index

                # Previous score stored to compare with next score 
                lastScore = pointsComparer[index]["points"]

            # Adds points (Only for player)
            if int(values["ID"]) == int(playerid):
                addPoints(userid, possibleScores[previousPlayerPosition])


        # Updates all the points label
        self.pointsUpdater(userid)

        if self.isClient:
            endConnectionClient()
        else:
            endConnectionServer()

        self.isClient = False
        self.isServer = False




# Displays webpage
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec_())
