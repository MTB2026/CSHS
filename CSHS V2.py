import time
import random
import sys

# Game State
playerVCOINS = 10000
inventory = []
hackedTargets = []
traceMeter = 0

def printSlow(text):
    for line in text.split('\n'):
        print(line)
        time.sleep(2)

def checkTrace():
    global traceMeter
    if traceMeter >= 100:
        printSlow("\n" + "!"*50)
        printSlow("[───] ALERT: TRACE METER AT 100% [───]")
        printSlow("[───] SYSTEM BREACHED: Cyber Police have located your IP address.")
        printSlow("[───] GAME OVER.")
        printSlow("!"*50 + "\n")
        sys.exit() 

def mainMenu():
    global playerVCOINS, traceMeter
    while True:
        checkTrace() 
        
        print("\n" + "="*37)
        print(f" VIRTUAL TERMINAL v1.5 | VCoins: {playerVCOINS} ")
        print(f" SYSTEM TRACE LEVEL: {traceMeter}% ")
        print("="*37)
        print(" 1. Dark Pool (Buy Tools)")
        print(" 2. Available Targets (Hack Servers)")
        print(" 3. View Inventory")
        print(" 4. Terminate connection (Exit Game)")
        
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
            print("\n[!] Invalid command.")

def darkPool():
    global playerVCOINS
    print("\n--- DARK POOL ---")
    print(f"Your Balance: {playerVCOINS} Vcoins")
    print(" 1. doorBreaker.exe (Cost: 200 VCoins) - Bypasses login screens")
    print(" 2. completelySafeFile.py  (Cost: 800 VCoins) - Overloads firewalls")
    print(" 3. wipeLogs.sh   (Cost: 1000 VCoins) - Reduces Trace by 35%")
    print(" 4. Return to Main Menu")
    
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
        global traceMeter
        if playerVCOINS >= 1000:
            playerVCOINS -= 1000
            traceMeter = max(0, traceMeter - 35)
            print(f"\n[+] Executed wipeLogs.sh. Trace dropped to {traceMeter}%.")
        else:
            print("\n[─] Insufficient VCoins.")
    elif choice == "4":
        return
    else:
        print("\n[!] Invalid choice or item already owned.")

def targetsList():
    print("\n--- AVAILABLE TARGETS ---")
    print(" 1. Airport Lounge Wi-Fi Router (Difficulty: Easy | Reward: 500 VCoins)")
    print(" 2. Waun Bank Mainframe         (Difficulty: Hard | Reward: 1500 VCoins)")
    print(" 3. Cancel")
    
    choice = input("\nscan@network:~# ").strip()
    
    if choice == "1":
        hackAirport()
    elif choice == "2":
        hackWaun()
    elif choice == "3":
        return
    else:
        print("\n[!] Target lost.")

def hackAirport():
    global playerVCOINS, traceMeter
    if "Airport" in hackedTargets:
        print("\n[!] Network already compromised and drained of data.")
        return
        
    printSlow("\n[!] Connecting to Airport Lounge...\n[!] Gateway found. Scanning firewall...")
    
    pin = random.randint(100, 999)
    print(f"[!] Encryption Hint: Router ID includes sequence {pin}")
    attempt = input("Enter 3-digit router override PIN: ").strip()
    
    if attempt == str(pin):
        printSlow("[+] Access Granted!\n[+] Stealing data...")
        playerVCOINS += 500
        hackedTargets.append("Airport")

        traceMeter += 20
        print(f"[+] Hack Successful. Earned 500 VCoins. Trace increased by 20%.")
    else:
        printSlow("[─] ACCESS DENIED.\n[─] IP Flagged.")

        traceMeter += 45
        print("[!] Major security alert triggered! Trace spiked by 45%.")

def hackWaun():
    global playerVCOINS, traceMeter
    if "Waun" in hackedTargets:
        print("\n[!] Mainframe already wiped.")
        return
        
    printSlow("\n[!] Target: Waun Bank Core Systems.\n[!] WARNING: High security active.")
    
    if "doorBreaker.exe" not in inventory:
        printSlow("[─] Connection Terminated: Port 22 is securely locked.")
        traceMeter += 25
        print("[!] Automated firewall logged your connection attempt. Trace increased by 25%.")
        return
        
    printSlow("[+] Using doorBreaker.exe... Port 22 compromised.")
    
    if "completelySafeFile.py" not in inventory:
        printSlow("[─] Detection Alert! System Firewall caught your connection attempt.")
        traceMeter += 50
        print("[!] Hostile mainframe is aggressively counter-tracing you! Trace increased by 50%.")
        return
        
    printSlow("[+] Deploying completelySafeFile.py... Firewall crashed!\n[+] Downloading client list...")
    playerVCOINS += 1500
    hackedTargets.append("Waun")
    traceMeter += 40
    print(f"\n[+++] Hack Successful. Earned 1500 VCoins. Trace increased by 40%.")

printSlow("Initializing terminal...")
mainMenu()
