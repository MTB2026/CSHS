import random
import time
import sys

import os
from collections import Counter

# Constants 
saveFileName = "SAVE.txt"
timeLeft = 60 * 60
activeDeadline = None
runtimeState = None
policeChallengeActive = False
lastPoliceAlertAt = 0.0
duplicateCount = 0
failCount = 0
lastGame = ""
tempPen = None

# All of the targets available $$$ \/\/\/\/\/
# Stores the id, the name, the visible target name, the rewards, the trace gain, the amount of minigames and finally the difficulty
databaseOfTargets = [
    {"id": "Airport", "name": "Airport Lounge Wi-Fi Router", "reward": 500,
     "difficulty": "easy", "traceSuccess": 12, "traceFailure": 20,
     "requires": [], "minigameCount": 1},
    {"id": "Waun", "name": "Waun Bank Mainframe", "reward": 1500,
     "difficulty": "hard", "traceSuccess": 18, "traceFailure": 30,
     "requires": ["Airport"], "minigameCount": 2},
    {"id": "RealVertResearchServer", "name": "RealVert Research Server", "reward": 800,
     "difficulty": "easy", "traceSuccess": 10, "traceFailure": 20,
     "requires": ["Airport"], "minigameCount": 1},
    {"id": "RailroadHubNetwork", "name": "Railroad Hub Network", "reward": 1200,
     "difficulty": "medium", "traceSuccess": 12, "traceFailure": 25,
     "requires": ["RealVertResearchServer"], "minigameCount": 2},
    {"id": "StarchainNetwork", "name": "Starchain Network", "reward": 1400,
     "difficulty": "medium", "traceSuccess": 12, "traceFailure": 25,
     "requires": ["RealVertResearchServer"], "minigameCount": 2},
    {"id": "AllDataIncorporatedCloud", "name": "AllData Incorporated Cloud", "reward": 1800,
     "difficulty": "medium", "traceSuccess": 18, "traceFailure": 30,
     "requires": ["RailroadHubNetwork"], "minigameCount": 2},
    {"id": "GoldenVaultArchive", "name": "GoldenVault Archive", "reward": 2200,
     "difficulty": "hard", "traceSuccess": 18, "traceFailure": 30,
     "requires": ["StarchainNetwork"], "minigameCount": 3},
    {"id": "LiteExchangeDatabase", "name": "Lite Exchange Database", "reward": 2500,
     "difficulty": "hard", "traceSuccess": 18, "traceFailure": 32,
     "requires": ["AllDataIncorporatedCloud"], "minigameCount": 3},
    {"id": "ShadowDatabase", "name": "Shadow Database", "reward": 3000,
     "difficulty": "very hard", "traceSuccess": 20, "traceFailure": 35,
     "requires": ["GoldenVaultArchive", "LiteExchangeDatabase"], "minigameCount": 3},
    {"id": "GovernmentMainframe", "name": "Government Mainframe", "reward": 5000,
     "difficulty": "very hard", "traceSuccess": 0, "traceFailure": 40,
     "requires": ["ShadowDatabase"], "minigameCount": 3}
]

# All of the tool data \/\/\/\/\/
# Holds the name, cost, type and the description of the tool
databaseTools = [
    {"name": "doorBreaker.exe", "cost": 200, "type": "permanent",
     "description": "Required to access Waun Bank."},
    {"name": "completelySafeFile.py", "cost": 800, "type": "permanent",
     "description": "Required to access Waun Bank."},
    {"name": "wipeLogs.sh", "cost": 1000, "type": "consumable",
     "description": "Buy and use to reduce trace by 35 points."},
    {"name": "number.exe", "cost": 350, "type": "permanent",
     "description": "Shows a clue in Codebreaker."},
    {"name": "attemptAdd.py", "cost": 500, "type": "consumable",
     "description": "Adds one attempt to the next challenge."},
    {"name": "traceStop.exe", "cost": 900, "type": "consumable",
     "description": "Halves one failed minigame's trace penalty."},
    {"name": "moreMoney.exe", "cost": 1000, "type": "consumable",
     "description": "Adds 20% more Vcoins to the next successful target reward."},
    {"name": "findLogic.py", "cost": 650, "type": "permanent",
     "description": "Shows an extra clue in Path Finding or Pattern Analysis."},
    {"name": "forget.exe", "cost": 800, "type": "consumable",
     "description": "Cancels one minor minigame failure penalty."},
    {"name": "cipherSolve.py", "cost": 1100, "type": "permanent",
     "description": "Shows an extra clue in Cipher Buster."},
    {"name": "additionalTime.exe", "cost": 1400, "type": "consumable",
     "description": "Adds 120 seconds to the active timer."},
    {"name": "notADecoy.py", "cost": 1250, "type": "consumable",
     "description": "Cancels the next police tracking alert."}
]

# Checks if the timer has expired
def timerExpired():
    return activeDeadline is not None and time.monotonic() >= activeDeadline


# Fixes inputs so that they work as input() due to the conditions within the gameInput function which breaks it
def readTimedInput(prompt):
    return input(prompt)

# calculations that check if a police alert can happen
def maybePoliceAlert():
    global policeChallengeActive, lastPoliceAlertAt
    if runtimeState is None or policeChallengeActive or timerExpired():
        return
    trace = runtimeState["trace"]
    if trace >= 100:
        raise TimeoutError("trace")
    now = time.monotonic()
    if now - lastPoliceAlertAt < 75:
        return
    alertChance = min(0.30, 0.04 + (trace * 0.0025))
    if random.random() >= alertChance:
        return
    lastPoliceAlertAt = now
    policeChallengeActive = True
    try:
        printSlow("\n" + "!" * 48 + "\n[!] The hacker police are on your trail\n"
                  "[!] Complete a minigame to avoid gaining trace.\n" + "!" * 48)
        if runtimeState["toolUses"].get("notADecoy.py", 0) > 0:
            consumableUses("notADecoy.py", runtimeState["toolUses"])
            print("[+] notADecoy.py spoofed the tracking signal. Alert cancelled.")
            return
        trace = runtimeState["trace"]
        if trace < 35:
            difficulty = "easy"
        elif trace < 70:
            difficulty = "medium"
        else:
            difficulty = "hard"
        print("Defence difficulty:", difficulty)
        passed = playRandomMinigame(difficulty, runtimeState["inventory"],
                                    runtimeState["toolUses"])
        if passed:
            print("[+] Tracking signal blocked. No trace added.")
        else:
            penalty = random.randint(15, 25)
            print("[!] Minigame failed, trace added.", penalty, "% trace.")
            trace = traceGain(runtimeState["trace"], penalty,
                             runtimeState["inventory"], runtimeState["toolUses"])
            runtimeState["trace"] = trace
            if trace >= 100:
                raise TimeoutError("trace")
    finally:
        policeChallengeActive = False

# Checks the timer and police events before allowing an input from the user
def gameInput(prompt):
    if timerExpired():
        print("\n[!] Your time has expired.")
        raise TimeoutError("timer")
    maybePoliceAlert()
    if runtimeState is not None and runtimeState["trace"] >= 100:
        raise TimeoutError("trace")
    answer = readTimedInput(prompt)
    if timerExpired():
        print("\n[!] Your time has expired.")
        raise TimeoutError("timer")
    return answer

def printSlow(message):
    for line in message.split("\n"):
        print(line)
        time.sleep(0.15)

# Keeps trace ebtween 0 and 100 so there are no errors
def tempTrace(trace):
    return max(0, min(100, int(trace)))

def findTool(toolName):
    for tool in databaseTools:
        if tool["name"] == toolName:
            return tool
    return None

def getsecondsRemaining():
    if activeDeadline is None:
        if runtimeState is not None:
            return max(0, int(runtimeState.get("secondsRemaining", timeLeft)))
        return timeLeft
    return max(0, int(activeDeadline - time.monotonic()))

# reds the save file and changes it depending on what is new within the current state of the game
def saveGame(Vcoins, trace, inventory, completed, toolUses=None):
    if toolUses is None:
        toolUses = {}
    secondsRemaining = getsecondsRemaining()
    try:
        with open(saveFileName, "w", encoding="utf-8") as saveFile:
            saveFile.write(str(Vcoins) + "\n")
            saveFile.write(str(tempTrace(trace)) + "\n")
            saveFile.write(",".join(inventory) + "\n")
            saveFile.write(",".join(completed) + "\n")
            saveFile.write(",".join(
                toolName + ":" + str(amount)
                for toolName, amount in toolUses.items()
            ) + "\n")
            saveFile.write(str(secondsRemaining) + "\n")
            saveFile.write(str(duplicateCount) + "\n")
            saveFile.write(str(failCount) + "\n")
        if runtimeState is not None:
            runtimeState["secondsRemaining"] = secondsRemaining
        print("\n[+] Save file updated successfully. Time remaining:",
              str(secondsRemaining // 60) + " minutes.")
    except (OSError, ValueError) as error:
        print("\n[!] Could not save the game:", error)

# Resets save after winning or losing
def clearSave():
    global duplicateCount, failCount
    duplicateCount = 0
    failCount = 0
    try:
        with open(saveFileName, "w", encoding="utf-8") as saveFile:
            saveFile.write("10000\n0\n\n\n\n" + str(timeLeft) + "\n0\n0\n")
        print("[+] Save file reset.")
    except OSError as error:
        print("[!] Could not reset the save file:", error)


# reads from the save file to load data
def loadSave():
    try:
        with open(saveFileName, "r", encoding="utf-8") as saveFile:
            lines = saveFile.read().splitlines()
        if len(lines) != 8:
            raise ValueError("Save file is invalid.")
        Vcoins = max(0, int(lines[0]))
        trace = tempTrace(int(lines[1]))
        inventory = [item for item in lines[2].split(",") if item]
        completed = [item for item in lines[3].split(",") if item]
        toolUses = {}
        
        if lines[4]:
            for entry in lines[4].split(","):
                toolName, amountText = entry.rsplit(":", 1)
                toolUses[toolName] = max(0, int(amountText))
        secondsRemaining = max(0, int(lines[5]))
        savedDuplicateCount = max(0, int(lines[6]))
        savedFailCount = max(0, int(lines[7]))
        print("\n[+] Existing profile loaded.")
        return (Vcoins, trace, inventory, completed, toolUses, secondsRemaining,
                savedDuplicateCount, savedFailCount)
    except FileNotFoundError:
        print("\n[!] No save found. Creating a new save file.")
    except (OSError, ValueError, IndexError) as error:
        print("\n[!] Save could not be read:", error)
        print("[!] Creating a save file.")
    return 10000, 0, [], [], {}, timeLeft, 0, 0

def toolEquipped(inventory, toolName):
    return toolName in inventory

def consumableUses(toolName, toolUses):
    if toolUses.get(toolName, 0) > 0:
        toolUses[toolName] -= 1
        if toolUses[toolName] <= 0:
            del toolUses[toolName]
        return True
    
    return False

# Trace addition logic
def traceGain(trace, amount, inventory, toolUses, minorFailure=False):
    global runtimeState
    originalTrace = tempTrace(trace)
    if minorFailure and toolUses.get("forget.exe", 0) > 0:
        if consumableUses("forget.exe", toolUses):
            print("[+] forget.exe cancelled the trace gain.")
            updatedTrace = originalTrace
            if runtimeState is not None:
                runtimeState["trace"] = updatedTrace
            print("Trace gained: 0%. Current trace: " + str(updatedTrace) + "%.")
            return updatedTrace
    if toolUses.get("traceStop.exe", 0) > 0:
        if consumableUses("traceStop.exe", toolUses):
            amount = amount // 2
            print("[+] traceStop.exe halved the trace gained.")
            
    updatedTrace = tempTrace(originalTrace + amount)
    actualGain = updatedTrace - originalTrace
    if runtimeState is not None:
        runtimeState["trace"] = updatedTrace
    print("Trace gained: " + str(actualGain) + "%. Current trace: "
          + str(updatedTrace) + "%.")
    return updatedTrace

def inventorySpace(inventory, toolUses):
    print("\n--- INVENTORY ---")
    displayedTools = list(inventory)
    for toolName, amount in toolUses.items():
        if amount > 0 and toolName not in displayedTools:
            displayedTools.append(toolName)
    if not displayedTools:
        print("You have no tools.")
        return
    for toolName in displayedTools:
        if findTool(toolName) and findTool(toolName)["type"] == "consumable":
            print("- " + toolName + " (charges: " + str(toolUses.get(toolName, 0)) + ")")
        else:
            print("- " + toolName)


# Dark pool shop code
def darkPool(Vcoins, trace, inventory, toolUses):
    while True:
        print("\n--- DARK POOL ---")
        print("Balance:", Vcoins, "Vcoins")
        for index, tool in enumerate(databaseTools, 1):
            if tool["type"] == "permanent" and tool["name"] in inventory:
                status = "OWNED"
            elif tool["type"] == "consumable":
                status = "charges: " + str(toolUses.get(tool["name"], 0))
            else:
                status = "available"
            print(str(index) + ". " + tool["name"] + " (" + str(tool["cost"])
                  + " Vcoins) - " + tool["description"] + " [" + status + "]")
        print(str(len(databaseTools) + 1) + ". Return")
        choice = gameInput("\nbuy@darkpool:~# ").strip()
        if runtimeState is not None:
            trace = runtimeState["trace"]
        if not choice.isdigit():
            print("Please enter a menu number.")
            continue
        
        choiceNumber = int(choice)
        if choiceNumber == len(databaseTools) + 1:
            break
        if choiceNumber < 1 or choiceNumber > len(databaseTools):
            print("Invalid selection.")
            continue
        tool = databaseTools[choiceNumber - 1]
        toolName = tool["name"]
        if tool["type"] == "permanent" and toolName in inventory:
            print("You already own that tool.")
            continue
        if Vcoins < tool["cost"]:
            print("Insufficient Vcoins.")
            continue
        Vcoins -= tool["cost"]
        if tool["type"] == "permanent":
            inventory.append(toolName)
            print("[+] Purchased", toolName)
        else:
            toolUses[toolName] = toolUses.get(toolName, 0) + 1
            print("[+] Added one charge of", toolName)
        if toolName == "additionalTime.exe":
            if consumableUses("additionalTime.exe", toolUses):
                global activeDeadline
                if activeDeadline is not None:
                    activeDeadline += 120
                if runtimeState is not None:
                    runtimeState["secondsRemaining"] = getsecondsRemaining()
                print("[+] Timer extended by 120 seconds.")
        if toolName == "wipeLogs.sh":
            trace = tempTrace(trace - 35)
            toolUses["wipeLogs.sh"] -= 1
            if toolUses["wipeLogs.sh"] <= 0:
                del toolUses["wipeLogs.sh"]
            print("[+] Trace reduced to", trace, "%.")
            if runtimeState is not None:
                runtimeState["trace"] = trace
    if runtimeState is not None:
        runtimeState["trace"] = trace
    return Vcoins, trace, inventory, toolUses



# Minigame difficulty logic
def getDifficultySettings(difficulty):
    if difficulty == "easy":
        return 5, 3
    if difficulty == "medium":
        return 4, 4
    if difficulty == "hard":
        return 3, 5
    return 2, 6

# All minigame logic below
def playCodebreaker(difficulty, inventory):
    global duplicateCount, failCount, tempPen
    duplicateCount += 1
    tempPen = None
    digits = 5
    attempts = 8
    digitsSelected = [random.choice("0123456789") for d in range(digits)]
    if duplicateCount % 4 == 0 and len(set(digitsSelected)) == digits:
        digitsSelected[-1] = digitsSelected[0]
    currentCode = "".join(digitsSelected)
    print("\n[MINIGAME] Codebreaker")
    print("Guess the 5 digit code. You have 8 attempts.")
    print("Digits can be any number from 0 to 9")
    if toolEquipped(inventory, "number.exe"):
        print("[number.exe] Hint: the code ends in", currentCode[-1] + ".")
    attemptsUsed = 0
    
    while attemptsUsed < attempts:
        guess = gameInput("Code guess: ").strip()
        if not guess.isdigit() or len(guess) != digits:
            print("Enter exactly 5 digits. This does not use an attempt.")
            continue
        attemptsUsed += 1
        relay = [None] * digits
        remainingDigits = Counter()
        for position in range(digits):
            if guess[position] == currentCode[position]:
                relay[position] = "CORRECT POSITION"
            else:
                remainingDigits[currentCode[position]] += 1
        for position in range(digits):
            if relay[position] == "CORRECT POSITION":
                continue
            guessedDigit = guess[position]
            if remainingDigits[guessedDigit] > 0:
                relay[position] = "WRONG POSITION"
                remainingDigits[guessedDigit] -= 1
            else:
                relay[position] = "NOT IN CODE"
        print("relay for this guess:")
        for position, status in enumerate(relay, 1):
            print("  Position", position, "(" + guess[position - 1] + "): " + status)
        if guess == currentCode:
            print("[+] Code accepted.")
            return True
    print("[!] Out of attempts. The code was", currentCode)
    failCount += 1
    if failCount == 1:
        tempPen = 5
    elif failCount == 2:
        tempPen = 7
    return False

# Clear screen. Doens't work as intended, will fix later (maybe)
def clearTerminal():
    if os.name == "nt":
        os.system("cls")
    else:
        print("\033[3J\033[2J\033[H", end="", flush=True)
        os.system("clear")

def playNumberMemory(difficulty, inventory, toolUses):
    sequenceLength = {"easy": 3, "medium": 4, "hard": 5, "very hard": 6}[difficulty]
    sequence = "".join(str(random.randint(0, 9)) for s in range(sequenceLength))
    print("\n[MINIGAME] Remember The Number")
    print("Memorise this sequence. It will disappear in 3 seconds:")
    print("\n      " + sequence + "\n")
    time.sleep(3)
    clearTerminal()
    print("[MINIGAME] Remember The Number")
    print("The sequence has disappeared. Enter it from memory.")
    extraAttempt = 0
    
    if consumableUses("attemptAdd.py", toolUses):
        extraAttempt = 1
        print("[+] attemptAdd.py added one attempt.")
    for attemptNumber in range(1 + extraAttempt):
        answer = gameInput("Enter the sequence: ").strip()
        if answer == sequence:
            print("[+] Signal matched.")
            return True
        print("Incorrect sequence.")
    print("The sequence was", sequence)
    return False

def playPathFinding(difficulty, inventory):
    print("\n[MINIGAME] Path Finding")
    print("Two possible paths are shown. Add the numbers on each path.")
    print("The stable path is the one whose total equals the target value.")
    pathLength = {"easy": 2, "medium": 3, "hard": 4, "very hard": 5}[difficulty]
    validPath = [random.randint(1, 9) for c in range(pathLength)]
    targetTotal = sum(validPath)
    invalidPath = [random.randint(1, 9) for c in range(pathLength)]
    while sum(invalidPath) == targetTotal:
        invalidPath = [random.randint(1, 9) for c in range(pathLength)]
    if random.choice([True, False]):
        pathA, pathB, answer = validPath, invalidPath, "A"
    else:
        pathA, pathB, answer = invalidPath, validPath, "B"
    print("Total to reach:", targetTotal)
    print("Path A:", " -> ".join(str(value) for value in pathA),
          "(total:", sum(pathA), ")")
    print("Path B:", " -> ".join(str(value) for value in pathB),
          "(total:", sum(pathB), ")")
    print("Choose the path that reaches the total.")
    if toolEquipped(inventory, "findLogic.py"):
        print("[findLogic.py] Hint: compare each paths's total with", targetTotal, ".")
    guess = gameInput("Stable path (A/B): ").strip().upper()
    return guess == answer

def playCipherBuster(difficulty, inventory):
    words = {"easy": ("FDW", "CAT"), "medium": ("KRPH", "HOME"),
             "hard": ("VHFUHW", "SECRET"), "very hard": ("SURMHFW", "PROJECT")}
    codedWord, answer = words[difficulty]
    print("\n[MINIGAME] Cipher Buster")
    print("Decode this cipher:", codedWord)
    print("Each letter has been shifted forward by 3.")
    if toolEquipped(inventory, "cipherSolve.py"):
        print("[cipherSolve.py] Hint: the answer begins with", answer[0] + ".")
    guess = gameInput("Decoded word: ").strip().upper()
    return guess == answer



def playBIDMAS(difficulty):
    print("\n[MINIGAME] BIDMAS")
    if difficulty == "easy":
        firstNumber = random.randint(4, 25)
        secondNumber = random.randint(3, 20)
        question = "What is " + str(firstNumber) + " + " + str(secondNumber) + "? "
        answer = firstNumber + secondNumber
    elif difficulty == "medium":
        firstNumber = random.randint(4, 12)
        secondNumber = random.randint(3, 9)
        thirdNumber = random.randint(2, 20)
        question = "What is " + str(firstNumber) + " x " + str(secondNumber) + " - " + str(thirdNumber) + "? "
        answer = firstNumber * secondNumber - thirdNumber
    elif difficulty == "hard":
        firstNumber = random.randint(5, 18)
        secondNumber = random.randint(2, 9)
        thirdNumber = random.randint(4, 25)
        question = "What is (" + str(firstNumber) + " x " + str(secondNumber) + ") + " + str(thirdNumber) + "? "
        answer = (firstNumber * secondNumber) + thirdNumber
    else:
        firstNumber = random.randint(6, 18)
        secondNumber = random.randint(4, 12)
        thirdNumber = random.randint(2, 8)
        fourthNumber = random.randint(3, 15)
        question = "What is (" + str(firstNumber) + " x " + str(secondNumber) + ") - (" + str(thirdNumber) + " x " + str(fourthNumber) + ")? "
        answer = (firstNumber * secondNumber) - (thirdNumber * fourthNumber)
    userAnswer = gameInput(question).strip()
    if userAnswer.lstrip("-").isdigit() and int(userAnswer) == answer:
        return True
    print("Incorrect. The answer was", answer)
    return False

def playPatternAnalysis(difficulty, inventory):
    patternData = {
        "easy": [
            ("2, 4, 6, 8, ?", "10"),
            ("5, 10, 15, 20, ?", "25"),
            ("1, 3, 5, 7, ?", "9"),
            ("10, 9, 8, 7, ?", "6"),
            ("3, 6, 9, 12, ?", "15"),
            ("1, 2, 4, 8, ?", "16")
        ],
        "medium": [
            ("3, 6, 12, 24, ?", "48"),
            ("4, 7, 10, 13, ?", "16"),
            ("2, 5, 10, 17, ?", "26"),
            ("81, 27, 9, 3, ?", "1"),
            ("1, 4, 9, 16, ?", "25"),
            ("2, 6, 18, 54, ?", "162")
        ],
        "hard": [
            ("1, 4, 9, 16, ?", "25"),
            ("2, 5, 11, 23, ?", "47"),
            ("3, 8, 15, 24, ?", "35"),
            ("1, 1, 2, 3, 5, 8, ?", "13"),
            ("100, 90, 73, 49, ?", "18"),
            ("2, 3, 5, 9, 17, ?", "33")
        ],
        "very hard": [
            ("2, 3, 5, 8, 12, ?", "17"),
            ("1, 2, 6, 24, 120, ?", "720"),
            ("4, 9, 19, 39, 79, ?", "159"),
            ("2, 6, 12, 20, 30, ?", "42"),
            ("1, 4, 10, 20, 35, ?", "56"),
            ("7, 14, 12, 24, 22, ?", "44")
        ]
    }
    sequence, answer = random.choice(patternData[difficulty])
    print("\n[MINIGAME] Pattern Analysis")
    print("Complete the sequence:", sequence)
    if toolEquipped(inventory, "findLogic.py"):
        print("[findLogic.py] Hint: the next value is", answer + ".")
    return gameInput("Missing value: ").strip() == answer

# how the code decides what minigame to use
def playRandomMinigame(difficulty, inventory, toolUses):
    global lastGame, tempPen
    tempPen = None
    minigames = [
        ("Codebreaker", lambda: playCodebreaker(difficulty, inventory)),
        ("Number Memory", lambda: playNumberMemory(difficulty, inventory, toolUses)),
        ("Path Finding", lambda: playPathFinding(difficulty, inventory)),
        ("Cipher Buster", lambda: playCipherBuster(difficulty, inventory)),
        ("BIDMAS", lambda: playBIDMAS(difficulty)),
        ("Pattern Analysis", lambda: playPatternAnalysis(difficulty, inventory))
    ]
    gameName, gameFunction = random.choice(minigames)
    lastGame = gameName
    print("[Challenge selected:", gameName + "]")
    return gameFunction()


# Changes player state depending on outcome from the player
def runTarget(target, Vcoins, trace, inventory, completed, toolUses):
    targetId = target["id"]
    if targetId in completed:
        print("\n[!] Target already completed.")
        return Vcoins, trace, completed
    missingTargets = [required for required in target["requires"]
                      if required not in completed]
    if missingTargets:
        print("\n[!] Target locked. Complete first:", ", ".join(missingTargets))
        return Vcoins, trace, completed
    
    if targetId == "Waun":
        if not toolEquipped(inventory, "doorBreaker.exe"):
            print("[!] Waun Bank requires doorBreaker.exe.")
            return Vcoins, trace, completed
        if not toolEquipped(inventory, "completelySafeFile.py"):
            print("[!] Waun Bank requires completelySafeFile.py.")
            return Vcoins, trace, completed
    printSlow("\n[!] Connecting to " + target["name"] + "...")
    passedAll = True
    usedMinigames = []
    for stageNumber in range(target["minigameCount"]):
        if targetId == "GovernmentMainframe":
            difficulty = "very hard"
        elif target["difficulty"] == "very hard":
            difficulty = "very hard"
        elif target["difficulty"] == "hard":
            difficulty = random.choice(["hard", "very hard"])
        elif target["difficulty"] == "medium":
            difficulty = random.choice(["medium", "hard"])
        else:
            difficulty = random.choice(["easy", "medium"])
        print("\nChallenge", stageNumber + 1, "of", target["minigameCount"],
              "- difficulty:", difficulty)
        if playRandomMinigame(difficulty, inventory, toolUses):
            trace = runtimeState["trace"] if runtimeState is not None else trace
            print("[+] Challenge passed.")
        else:
            trace = runtimeState["trace"] if runtimeState is not None else trace
            print("[!] Challenge failed.")
            if (lastGame == "Codebreaker"
                    and tempPen is not None):
                penalty = tempPen
                print("[!] Failed Codebreaker challenge penalty:", penalty, "% trace.")
                minorFailure = True
            else:
                penalty = target["traceFailure"]
                minorFailure = target["difficulty"] in ["easy", "medium"]
            trace = traceGain(trace, penalty, inventory, toolUses,
                             minorFailure=minorFailure)
            if runtimeState is not None:
                runtimeState["trace"] = trace
            passedAll = False
            break
    
    if passedAll:
        reward = target["reward"]
        if consumableUses("moreMoney.exe", toolUses):
            bonus = int(reward * 0.20)
            reward += bonus
            print("[+] moreMoney.exe bonus:", bonus, "Vcoins.")
        Vcoins += reward
        oldTrace = tempTrace(trace)
        trace = tempTrace(trace + target["traceSuccess"])
        actualGain = trace - oldTrace
        if runtimeState is not None:
            runtimeState["trace"] = trace
        print("Trace gained: " + str(actualGain) + "%. Current trace: "
              + str(trace) + "%.")
        completed.append(targetId)
        printSlow("[+] Target compromised. Reward: " + str(reward) + " Vcoins.")
        if targetId == "GovernmentMainframe":
            printSlow("\n" + "=" * 48 + "\nGovernment Mainframe Hacked\nYOU WIN!\n" + "=" * 48)
    else:
        print("[!] Target escaped. No reward was paid.")
    return Vcoins, trace, completed

# Target list availability
def targetList(Vcoins, trace, inventory, completed, toolUses):
    while True:
        print("\n--- AVAILABLE TARGETS ---")
        for index, target in enumerate(databaseOfTargets, 1):
            if target["id"] in completed:
                status = "COMPLETED"
            elif all(required in completed for required in target["requires"]):
                status = "AVAILABLE"
            else:
                status = "LOCKED"
            print(str(index) + ". " + target["name"] + " (Reward: "
                  + str(target["reward"]) + " Vcoins) [" + status + "]")
        print(str(len(databaseOfTargets) + 1) + ". Return")
        choice = gameInput("\nscan@network:~# ").strip()
        if runtimeState is not None:
            trace = runtimeState["trace"]
        if not choice.isdigit():
            print("Please enter a menu number.")
            continue
        choiceNumber = int(choice)
        if choiceNumber == len(databaseOfTargets) + 1:
            break
        if choiceNumber < 1 or choiceNumber > len(databaseOfTargets):
            print("Invalid selection.")
            continue
        Vcoins, trace, completed = runTarget(
            databaseOfTargets[choiceNumber - 1], Vcoins, trace,
            inventory, completed, toolUses
        )
        if runtimeState is not None:
            trace = runtimeState["trace"] = trace
        if "GovernmentMainframe" not in completed:
            saveGame(Vcoins, trace, inventory, completed, toolUses)
        if trace >= 100 or "GovernmentMainframe" in completed:
            break
    return Vcoins, trace, completed

def showGameOver(trace):
    printSlow("\n" + "!" * 48
              + "\n[!] Trace meter at 100%\n[!] GAME OVER\n"
              + "!" * 48)

# Main menu 
def mainMenu():
    global activeDeadline, runtimeState, lastPoliceAlertAt, duplicateCount, failCount
    (Vcoins, trace, inventory, completed, toolUses, secondsRemaining,
     duplicateCount, failCount) = loadSave()
    secondsRemaining = max(0, secondsRemaining)
    activeDeadline = time.monotonic() + secondsRemaining
    lastPoliceAlertAt = time.monotonic()
    runtimeState = {
        "trace": trace,
        "inventory": inventory,
        "toolUses": toolUses,
        "secondsRemaining": secondsRemaining
    }
    
    try:
        while True:
            trace = tempTrace(runtimeState["trace"])
            secondsRemaining = getsecondsRemaining()
            runtimeState["secondsRemaining"] = secondsRemaining
            if timerExpired() or secondsRemaining <= 0:
                printSlow("\n" + "!" * 48
                          + "\n[!] Your time expired\n[!] GAME OVER\n"
                          + "!" * 48)
                clearSave()
                break
            if trace >= 100:
                showGameOver(trace)
                clearSave()
                break
            if "GovernmentMainframe" in completed:
                printSlow("\n" + "=" * 48
                          + "\nGoverment Mainframe Hacked\nYOU WIN!\n"
                          + "=" * 48)
                saveGame(Vcoins, trace, inventory, completed, toolUses)
                break
            minutesLeft = secondsRemaining // 60
            secondsLeft = secondsRemaining % 60
            print("\n" + "=" * 46)
            print(" VIRTUAL TERMINAL v5.0 | Vcoins:", Vcoins)
            print(" SYSTEM TRACE LEVEL:", str(trace) + "%")
            print(" TIME REMAINING: " + str(minutesLeft) + "m "
                  + str(secondsLeft) + "s")
            print(" TARGETS COMPLETED:", str(len(completed)) + "/" + str(len(databaseOfTargets)))
            print("=" * 46)
            print("1. Dark Pool (Buy Tools)")
            print("2. Available Targets (Hack Servers)")
            print("3. View Inventory")
            print("4. Manual Save")
            print("5. Terminate connection (Exit Game)")
            choice = gameInput("\nroot@VT:~# ").strip()
            trace = runtimeState["trace"]
            if choice == "1":
                Vcoins, trace, inventory, toolUses = darkPool(
                    Vcoins, trace, inventory, toolUses)
            elif choice == "2":
                Vcoins, trace, completed = targetList(
                    Vcoins, trace, inventory, completed, toolUses)
                if "GovernmentMainframe" in completed:
                    print("[+] Game Complete...")
                    clearSave()
                    break
            elif choice == "3":
                inventorySpace(inventory, toolUses)
            elif choice == "4":
                saveGame(Vcoins, trace, inventory, completed, toolUses)
            elif choice == "5":
                saveGame(Vcoins, trace, inventory, completed, toolUses)
                printSlow("\n[.] Connection terminated.\n[.] Progress saved. See you soon.")
                break
            else:
                print("Invalid choice. Select 1 to 5.")
            trace = tempTrace(runtimeState["trace"] if runtimeState is not None else trace)
            if trace >= 100:
                showGameOver(trace)
                clearSave()
                break
            
    except TimeoutError as reason:
        if str(reason) == "timer":
            printSlow("\n" + "!" * 48
                      + "\n[!] Your time has expired\n[!] GAME OVER\n"
                      + "!" * 48)
        else:
            showGameOver(runtimeState["trace"] if runtimeState is not None else trace)
        clearSave()
    finally:
        activeDeadline = None
        runtimeState = None

printSlow("Initializing terminal...")
mainMenu()

# Hopefully there aren't any bugs within the code
# To anyone who does find bugs, comment on the repository
# explaining what the bug is and how you managed to get it. Or, sending me a screenshot
# of it fixed by you (would save me some time if you did ^.^)
