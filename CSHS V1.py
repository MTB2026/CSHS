import time
import random

# Game State
playerVCOINS = 10000
inventory = []
hackedTargets = []

def printSlow(text):
    # Prints text with a delay like inside of a terminal
    for line in text.split('\n'):
        print(line)
        time.sleep(2)

def mainMenu():
    global playerVCOINS
    while True:
        print("\n" + "="*37)
        print(f" VIRTUAL TERMINAL v1.4 | VCoins: {playerVCOINS} ")
        print("="*37)
        print("[1] Dark Pool (Buy Tools)")
        print("[2] Available Targets (Hack Servers)")
        print("[3] View Inventory")
        print("[4] Terminate connection (Exit Game)")
        
        choice = input("\nroot@VT:~# ").strip()
        
        if choice == "1":
            darkPool()
        elif choice == "2":
            targetsList()
        elif choice == "3":
            print(f"\n[.] Available Tools: {', '.join(inventory) if inventory else 'None'}")
        elif choice == "4":
            printSlow("\n[.] Connection terminated...\n[.] Traces wiped. See you soon.")
            break
        else:
            print("\n[.] Invalid command.")

def darkPool():
    global playerVCOINS
    print("\n--- DARK POOL ---")
    print(f"Your Balance: {playerVCOINS} VCoins")
    print("[1] doorBreaker.exe (Cost: 200 VCoins) - Bypasses login screens")
    print("[2] completelySafeFile.py  (Cost: 800 VCoins) - Overloads firewalls")
    print("[3] Return to Main Menu")
    
    choice = input("\nbuy@darkpool:~# ").strip()
    
    if choice == "1" and "doorBreaker.exe" not in inventory:
        if playerVCOINS >= 200:
            playerVCOINS -= 200
            inventory.append("doorBreaker.exe")
            print("\n[+] Downloaded: doorBreaker.exe")
        else:
            print("\n[─] Insufficient VCoins.")
    elif choice == "2" and "completelySafeFile.py" not in inventory:
        if playerVCOINS >= 800:
            playerVCOINS -= 800
            inventory.append("completelySafeFile.py")
            print("\n[+] Downloaded: completelySafeFile.py")
        else:
            print("\n[─] Insufficient VCoins.")
    elif choice == "3":
        return
    else:
        print("\n[.] Invalid choice or item already owned.")

def targetsList():
    print("\n--- AVAILABLE TARGETS ---")
    print("[1] Airport Lounge Wi-Fi Router (Difficulty: Easy | Reward: 500 VCoins)")
    print("[2] Waun Bank Mainframe         (Difficulty: Hard | Reward: 1500 VCoins)")
    print("[3] Cancel")
    
    choice = input("\nscan@network:~# ").strip()
    
    if choice == "1":
        hackAirport()
    elif choice == "2":
        hackWaun()
    elif choice == "3":
        return
    else:
        print("\n[.] Target lost.")

def hackAirport():
    global playerVCOINS
    if "Airport" in hackedTargets:
        print("\n[.] Network already compromised and drained of data.")
        return
        
    printSlow("\n[.] Connecting to Airport Lounge...\n[.] Gateway found. Scanning firewall...")
    
    # Quick text-based puzzle
    pin = random.randint(100, 999)
    print(f"[.] Encryption Hint: Router ID includes sequence {pin}")
    attempt = input("Enter 3-digit router override PIN: ").strip()
    
    if attempt == str(pin):
        printSlow("[+] Access Granted.\n[+] Stealing data...")
        playerVCOINS += 500
        hackedTargets.append("Airport")
        print(f"[+] Hack Successful. Earned 500 VCoins.")
    else:
        printSlow("[─] ACCESS DENIED.\n[─] IP Flagged. Connection lost.")

def hackWaun():
    global playerVCOINS
    if "Waun" in hackedTargets:
        print("\n[.] Mainframe already wiped.")
        return
        
    printSlow("\n[.] Target: Waun Bank Core Systems.\n[.] WARNING: High security active.")
    
    # Level 1 Gate: Requires Dark Pool Item
    if "doorBreaker.exe" not in inventory:
        printSlow("[─] Connection Terminated: Port 22 is securely locked.\n[Hint: Check Dark Pool for a completelySafeFile]")
        return
        
    printSlow("[+] Using doorBreaker.exe... Port 22 compromised.")
    
    # Level 2 Gate: Requires Second Item
    if "completelySafeFile.py" not in inventory:
        printSlow("[─] Detection Alert. System Firewall detected your trace.\n[Hint: You need a doorBreaker to overload the firewall]")
        return
        
    printSlow("[+] Deploying completelySafeFile.py... Firewall crashed.\n[+] Downloading client pins...")
    playerVCOINS += 1500
    hackedTargets.append("Waun")
    print(f"\n[+++] Hack Successful. Earned 1500 VCoins.")

# Start the game
printSlow("Initializing terminal...")
mainMenu()
