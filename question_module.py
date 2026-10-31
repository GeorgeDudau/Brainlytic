import sqlite3
import sympy 
from sympy.parsing.sympy_parser import parse_expr # Converts strings into sympy expressions

# Creates the question database
def questionDatabase():
    # Connects to the maths questions database
    connect = sqlite3.connect("mathQuestions.db")

    cursor = connect.cursor()

    # Creates the math questions database
    createTable = "CREATE TABLE IF NOT EXISTS mathQuestions(questionid INTEGER PRIMARY KEY AUTOINCREMENT, year INTEGER, imagePath TEXT UNIQUE, markschemePath TEXT, correctAnswer TEXT, marks INTEGER, timing INTEGER, type TEXT)"

    cursor.execute(createTable)

    # All maths questions to be used
    questions = [
    (2017, "mathQuestions/20171a.png", "mathQuestions/20171aMS.png", "1.635", 3, 180,"numerical"),
    (2017, "mathQuestions/20176a.png", "mathQuestions/20176aMS.png", "5/9*(9-x^2)", 3, 180,"algebra"),
    (2017, "mathQuestions/20177.png", "mathQuestions/20177MS.png", "1/4*e^4 - 5/4", 5, 300,"numerical"),
    (2017, "mathQuestions/20179.png", "mathQuestions/20179MS.png", "6", 5, 300,"numerical"),
    (2017, "mathQuestions/201711b.png", "mathQuestions/201711bMS.png", "7", 7, 600,"numerical"),

    (2018, "mathQuestions/20181.png", "mathQuestions/20181MS.png", "4/3", 3, 180,"numerical"),
    (2018, "mathQuestions/20183.png", "mathQuestions/20183MS.png", "root33", 4, 240,"numerical"),
    (2018, "mathQuestions/20188b.png", "mathQuestions/20188bMS.png", "10:46", 4, 240,"time"),
    (2018, "mathQuestions/20189b.png", "mathQuestions/20189bMS.png", "(-5root3, -5root3/3)", 5, 300,"coordinates"),


    (2019, "mathQuestions/20191.png", "mathQuestions/20191MS.png", "3", 3, 180,"numerical"),
    (2019, "mathQuestions/20193a.png", "mathQuestions/20193aMS.png", "10/(x-1)^3", 4, 240,"algebra"),
    (2019, "mathQuestions/20195a.png", "mathQuestions/20195aMS.png", "2*(x+1)^2+7", 2, 120,"algebra"),
    (2019, "mathQuestions/201913b.png", "mathQuestions/201913MS.png", "35*ln3 - 4.8*ln2", 8, 480,"numerical"),
    (2019, "mathQuestions/201914.png", "mathQuestions/201914MS.png", "1/8", 2, 120,"numerical"),

    (2020, "mathQuestions/202010.png", "mathQuestions/202010MS.png", "81.6", 2, 120,"numerical"),
    (2020, "mathQuestions/202015.png", "mathQuestions/202015MS.png", "i-8j+2k", 2, 120,"vector"),
    (2020, "mathQuestions/20202.png", "mathQuestions/20202MS.png", "ln(49/36)", 6, 360,"numerical"),
    (2020, "mathQuestions/20203.png", "mathQuestions/20203MS.png", "-18/(x^4+81)", 4, 240,"algebra"),

    (2021, "mathQuestions/20211.png", "mathQuestions/20211MS.png", "3", 3, 180,"numerical"),
    (2021, "mathQuestions/20216.png", "mathQuestions/20216MS.png", "-2i-3j-k", 2, 120,"vector"),
    (2021, "mathQuestions/20218.png", "mathQuestions/20218MS.png", "1000*e^(1/5*ln2)t", 4, 240,"algebra"),
    (2021, "mathQuestions/202111.png", "mathQuestions/202111MS.png", "14*(ln2)^2 - 12*ln2 + 4", 5, 300,"numerical"),
    (2021, "mathQuestions/202112.png", "mathQuestions/202112MS.png", "-1/300 *(x-90)^2 + 30", 5, 300,"algebra"),

    (2022, "mathQuestions/20221a.png", "mathQuestions/20221aMS.png", "(-2,-3)", 1, 60,"coordinates"),
    (2022, "mathQuestions/20224b.png", "mathQuestions/20224bMS.png", "ln9", 2, 120,"numerical"),
    (2022, "mathQuestions/202211b.png", "mathQuestions/202211bMS.png", "-4 + root33", 5, 300,"numerical"),
    (2022, "mathQuestions/202212.png", "mathQuestions/202212MS.png", "7/16 * e^8 + 1/16", 5, 300,"numerical"),
    ]

    cursor.executemany("INSERT OR IGNORE INTO mathQuestions (year, imagepath, markschemePath, correctAnswer, marks, timing, type) VALUES(?,?,?,?,?,?,?)", questions)
    connect.commit()
    connect.close()

# Retrieves the questions from the chosen year.
def questionRetrieval(year):
    # Connection to mathQuestions Database
    connect = sqlite3.connect("mathQuestions.db")

    cursor = connect.cursor()

    cursor.execute(
        "SELECT * FROM mathQuestions WHERE year = ? ORDER BY RANDOM() LIMIT 3",
        (year,)
    )

    questions = cursor.fetchall()

    connect.close()

    return questions

# Retrieves the question based on the ID
def questionRetrievalID(questionid):
        # Connection to mathQuestions Database
    connect = sqlite3.connect("mathQuestions.db")

    cursor = connect.cursor()

    cursor.execute(
        "SELECT * FROM mathQuestions WHERE questionid = ? ",
        (questionid,)
    )

    questions = cursor.fetchone()

    connect.close()

    return questions

# Nomalises the input so it can be understood by the sympy library and compared
def normaliseInput(expression):
    expression = expression.lower()
    expression = expression.replace("^","**")
    expression = expression.replace("root","sqrt")
    expression = expression.replace("√","sqrt")
    expression = expression.replace(" ","")
    expression = expression.replace(",","")
    expression = expression.replace("ln","log")
    expression = expression.replace("e","E")
    return expression

# Checks the answer depending on the question type
def mathAnswerChecker(userAnswer,answer,questionType):

    if questionType == "algebra":
        try:
            # Converts expression to sympy expressions
            userExpression = parse_expr(normaliseInput(userAnswer))
            answerExpression = parse_expr(normaliseInput(answer))

            # If they are the same answer then subtracting both will give 0
            check = userExpression.equals(answerExpression)
            if check:
                return True
            else:
                return False
            
        # In case the user has inputted the wrong data type
        except Exception:
            return False
        
    elif questionType == "numerical":
        try:
            # Converts expression to sympy expressions
            userExpression = parse_expr(normaliseInput(userAnswer))
            answerExpression = parse_expr(normaliseInput(answer))
            check = userExpression - answerExpression
            if check == 0:
                return True
            else:
                return False
        # In case the user has inputted the wrong data type
        except Exception:
            return False
        
    elif questionType == "vector":
        try:
            # String comparison between vectors (always simple)
            userExpression = normaliseInput(userAnswer)
            answerExpression = normaliseInput(answer)

            if userExpression == answerExpression:
                return True
            else: 
                return False
            
        except Exception:
            return False
    
    elif questionType == "coordinates":
        try:
            # gets rid of any brackets in the coordinate and gets the individual numbers
            userExpression = userExpression.replace("(","")
            userExpression = userExpression.replace(")","")
            userExpressionCoordinates = userExpression.split(",")

            answerExpression = answerExpression.replace("(","")
            answerExpression = answerExpression.replace(")","")
            answerExpressionCoordinates = userExpression.split(",")

            # Compares the numbers help in the x and y coordinate
            if userExpressionCoordinates[0] == answerExpressionCoordinates[0] and userExpressionCoordinates[1] == answerExpressionCoordinates[1]:
                return True
            else:
                return False
            
        # In case the user has inputted the wrong data type
        except Exception:
            return False
    
    elif questionType == "time":
        try:
            userExpressionTime = userExpression.split(":")
            answerExpressionTime =answerExpression.split(":")
            if userExpressionTime[0] == answerExpressionTime[0] and userExpressionTime[1] == answerExpressionTime[1]:
                return True
            else: 
                return False 
        except Exception:
            return False
    else: 
        return False





        

        


        



        


