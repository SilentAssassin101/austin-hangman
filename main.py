import sqlite3
import requests
import turtle

con = sqlite3.connect("game.db")
cur = con.cursor()
cur.execute(
    """CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY,
    status VARCHAR(30),
    fails INTEGER,
    word VARCHAR(30),
    revealedList VARCHAR(30),
    guessedList VARCHAR(30) )"""
)
con.commit()

alphabet = "abcdefghijklmnopqrstuvwxyz"


def checkGameInProgress():
    res = cur.execute("SELECT id FROM games WHERE status = 'inProgress'")
    if res.fetchone() is None:
        return False
    else:
        return True


def getCurrentGame():
    stat = ("inProgress",)
    res = cur.execute(
        """SELECT
        fails,
        word,
        revealedList,
        guessedList FROM games WHERE status = ?""",
        stat
    )
    result = res.fetchone()
    return result


def generateWord():
    url = 'https://random-word-api.vercel.app/api?words=1'
    try:
        words = requests.get(url)
    except Exception as e:
        print("error", e)
    return words.json()[0]


def createNewGame():
    cur.execute(
        """INSERT INTO games (
        status,
        fails,
        word,
        revealedList,
        guessedList
        ) VALUES (?, ?, ?, ?, ?) """,
        ("inProgress", 0, generateWord(), "", "")
    )
    con.commit()


def parseGame(currentGameResult):
    fails = currentGameResult[0]
    word = currentGameResult[1]
    revealedString = currentGameResult[2]
    guessedString = currentGameResult[3]
    revealedList = []
    for char in revealedString:
        revealedList.append(char)
    guessedList = []
    for char in guessedString:
        guessedList.append(char)
    reDict = {
        "fails": fails,
        "word": word,
        "revealedList": revealedList,
        "guessedList": guessedList
    }
    return reDict


def guessLetter(letter, guessedList: list[str], revealedList: list[str], word):
    if letter in guessedList:
        return 0, "Letter has Already Been Guessed"
    elif letter in word:
        revealedList.append(letter)
        guessedList.append(letter)
        print(showWord(word, revealedList))
        return 1, f"The letter {letter} was in the word"
    else:
        guessedList.append(letter)
        # TODO: Add part to hangman using turtle import
        print(showWord(word, revealedList))
        return 2, f"The letter {letter} was NOT in the word"


def showWord(word: str, revealedList: list[str]):
    revealedWord = ""
    for char in word:
        if char in revealedList:
            revealedWord += char
        else:
            revealedWord += "#"
    return revealedWord


def checkWin(word, revealedWord):
    if word == revealedWord:
        return True
    else:
        return False


def checkLoss(guessedList, revealedList):
    fails = checkNumFails(guessedList=guessedList, revealedList=revealedList)
    if fails >= 6:
        return True
    else:
        return False


def updateDatabase(
        fails: int,
        guessedList: list[str],
        revealedList: list[str]
):
    guessedString = ""
    revealedString = ""
    for char in guessedList:
        guessedString += char
    for char in revealedList:
        revealedString += char
    sql = """
    UPDATE games
    SET fails = ?,
    guessedList = ?,
    revealedList = ?
    WHERE status = ?"""
    params = (fails, guessedString, revealedString, "inProgress")
    cur.execute(sql, params)
    con.commit()


def checkNumFails(guessedList, revealedList):
    numFails = len(guessedList) - len(revealedList)
    return numFails


def askForLetter(guessedList: list[str]):
    guessedString = ""
    for letter in guessedList:
        guessedString += letter
    print(f"You have guessed the following letters: {guessedString}")
    while True:
        letter = input("Please enter a guess:")
        letter = letter.lower()
        if len(letter) != 1:
            print("The guess must be exactly 1 letter long")
        elif letter not in alphabet:
            print("The guess must be a letter")
        elif letter in guessedList:
            print("That letter has already been guessed")
        else:
            return letter


def printStats(gameStats):
    print(f"Lives remaining: {6 - gameStats['fails']}")
    print(showWord(gameStats["word"], gameStats["revealedList"]))


def gameLoop(gameStats):
    printStats(gameStats)
    guessedLetter = askForLetter(guessedList=gameStats["guessedList"])
    code, message = guessLetter(
        letter=guessedLetter,
        guessedList=gameStats["guessedList"],
        revealedList=gameStats["revealedList"],
        word=gameStats["word"]
    )
    match code:
        case 0:
            raise ValueError(message)
        case 1:
            # Good Guess
            print(message)
        case 2:
            # Bad Guess
            print(message)
            gameStats["fails"] += 1
            drawBodyPart(gameStats["fails"])


def endGame(wonOrLost, word):
    if wonOrLost not in ["won", "lost"]:
        raise TypeError(
            "Endgame function expected either won or lost as a parameter")
    cur.execute(
        """UPDATE games
        SET status = ?
        WHERE status = ?""",
        (wonOrLost, "inProgress")
    )
    con.commit()
    print(f"The word was \"{word}\"")
    print(f"You {wonOrLost}")
    exit()

# 573


def initializeDrawing():
    turtle.hideturtle()
    turtle.pu()
    turtle.goto(57.3, 57.3)
    turtle.pd()
    turtle.left(90)
    turtle.forward(100)
    turtle.left(90)
    turtle.forward(200)
    turtle.left(90)
    turtle.forward(500)


def drawHead():
    turtle.pu()
    turtle.home()
    turtle.pd()
    turtle.setheading(90)
    for i in range(36):
        turtle.forward(10)
        turtle.right(10)


def drawBody():
    turtle.pu()
    turtle.goto(57.3, -57.3)
    turtle.pd()
    turtle.setheading(270)
    turtle.forward(150)


def drawRightLeg():
    turtle.pu()
    turtle.goto(57.3, -207.3)
    turtle.pd()
    turtle.setheading(315)
    turtle.forward(80)


def drawLeftLeg():
    turtle.pu()
    turtle.goto(57.3, -207.3)
    turtle.pd()
    turtle.setheading(225)
    turtle.forward(80)


def drawRightArm():
    turtle.pu()
    turtle.goto(57.3, -127.3)
    turtle.pd()
    turtle.setheading(30)
    turtle.forward(80)


def drawLeftArm():
    turtle.pu()
    turtle.goto(57.3, -127.3)
    turtle.pd()
    turtle.setheading(150)
    turtle.forward(80)


def drawBodyPart(partNumber):
    match partNumber:
        case 1:
            drawHead()
        case 2:
            drawBody()
        case 3:
            drawRightLeg()
        case 4:
            drawLeftLeg()
        case 5:
            drawRightArm()
        case 6:
            drawLeftArm()


def main():
    if checkGameInProgress():
        print("Resuming last game")
    else:
        print("Starting a new game")
        createNewGame()
    gameStats = parseGame(getCurrentGame())
    initializeDrawing()
    fails: int = gameStats["fails"]
    if fails > 0:
        for i in range(1, (fails+1)):
            drawBodyPart(i)
    while True:
        gameLoop(gameStats)
        if checkWin(
            gameStats["word"],
            showWord(
                gameStats["word"],
                revealedList=gameStats["revealedList"])
        ):
            endGame("won", gameStats["word"])
        elif checkLoss(
                guessedList=gameStats["guessedList"],
                revealedList=gameStats["revealedList"]
        ):
            endGame("lost", gameStats["word"])
        else:
            updateDatabase(
                fails=checkNumFails(
                    guessedList=gameStats["guessedList"],
                    revealedList=gameStats["revealedList"]),
                guessedList=gameStats["guessedList"],
                revealedList=gameStats["revealedList"]
            )


if __name__ == "__main__":
    main()
