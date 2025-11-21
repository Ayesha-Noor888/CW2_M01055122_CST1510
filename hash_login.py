import bcrypt
import os
import re
import time
import secrets
import json

USER_DATA_FILE = "users.txt"
FAILED_ATTEMPTS_FILE = "failed_attempts.json"
SESSION_FILE = "sessions.json"
LOCKOUT_TIME = 300  # 5 minutes lockout in seconds


# Function 1: Hash Password

def hash_password(plain_text_password: str) -> str:
    password_bytes = plain_text_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")


# Function 2: Verify Password

def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    password_bytes = plain_text_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# Function 3: Check Password Strength

def check_password_strength(password: str) -> str:
    """
    Evaluates password strength as Weak, Medium, or Strong.
    """
    score = 0
    if len(password) >= 8:
        score += 1
    if re.search("[A-Z]", password):
        score += 1
    if re.search("[a-z]", password):
        score += 1
    if re.search("[0-9]", password):
        score += 1
    if re.search("[@#$%^&+=!]", password):
        score += 1

    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    else:
        return "Strong"


# Function 4: Check if User Exists

def user_exists(username: str) -> bool:
    if not os.path.exists(USER_DATA_FILE):
        return False
    with open(USER_DATA_FILE, "r") as f:
        next(f, None)
        for line in f:
            user, _, _ = line.strip().split(",", 2)
            if user == username:
                return True
    return False


# Function 5: Register User with Role

def register_user(username: str, password: str, role: str = "user") -> bool:
    if user_exists(username):
        print(f"\n Username '{username}' already exists.")
        return False

    hashed_password = hash_password(password)

    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "w") as f:
            f.write("username,password_hash,role\n")

    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{username},{hashed_password},{role}\n")

    print(f"\n User '{username}' registered successfully with role '{role}'.")
    print(f"Password Strength: {check_password_strength(password)}")
    return True


# Function 6: Create Session Token

def create_session(username: str) -> str:
    token = secrets.token_hex(16)
    session_data = {}
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            session_data = json.load(f)
    session_data[username] = {"token": token, "timestamp": time.time()}
    with open(SESSION_FILE, "w") as f:
        json.dump(session_data, f)
    return token

# --------------------------------------------------------------
# Function 7: Track Failed Login Attempts
# --------------------------------------------------------------
def track_failed_attempt(username: str) -> int:
    failed_data = {}
    if os.path.exists(FAILED_ATTEMPTS_FILE):
        with open(FAILED_ATTEMPTS_FILE, "r") as f:
            failed_data = json.load(f)

    if username not in failed_data:
        failed_data[username] = {"count": 1, "last_time": time.time()}
    else:
        last_time = failed_data[username]["last_time"]
        if time.time() - last_time > LOCKOUT_TIME:
            failed_data[username] = {"count": 1, "last_time": time.time()}
        else:
            failed_data[username]["count"] += 1
            failed_data[username]["last_time"] = time.time()

    with open(FAILED_ATTEMPTS_FILE, "w") as f:
        json.dump(failed_data, f)
    return failed_data[username]["count"]


# Function 8: Check Lockout

def is_locked(username: str) -> bool:
    if not os.path.exists(FAILED_ATTEMPTS_FILE):
        return False
    with open(FAILED_ATTEMPTS_FILE, "r") as f:
        failed_data = json.load(f)
    if username in failed_data:
        last_time = failed_data[username]["last_time"]
        count = failed_data[username]["count"]
        if count >= 3 and (time.time() - last_time) < LOCKOUT_TIME:
            return True
    return False


# Function 9: Login User with Lockout & Session

def login_user(username: str, password: str) -> bool:
    if is_locked(username):
        print("\n Account is locked. Try again later.")
        return False

    if not os.path.exists(USER_DATA_FILE):
        print("\nNo users registered yet.")
        return False

    with open(USER_DATA_FILE, "r") as f:
        next(f, None)
        for line in f:
            user, stored_hash, role = line.strip().split(",", 2)
            if user == username:
                if verify_password(password, stored_hash):
                    print(f"\n Login successful. Welcome, {username} ({role}).")
                    create_session(username)
                    return True
                else:
                    attempts = track_failed_attempt(username)
                    if attempts >= 3:
                        print("\n Incorrect password. Account locked for 5 minutes.")
                    else:
                        print(f"\n Incorrect password. Attempt {attempts}/3.")
                    return False

    print("\n Username not found.")
    return False


# Function 10: Main Menu

def display_menu():
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

def main():
    print("\nWelcome to the Secure Authentication System!")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == '1':
            username = input("Enter a username: ").strip()
            password = input("Enter a password: ").strip()
            role = input("Enter user role (user/admin/analyst): ").strip()
            register_user(username, password, role)
            input("\nPress Enter to return to main menu...")

        elif choice == '2':
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            login_user(username, password)
            input("\nPress Enter to return to main menu...")

        elif choice == '3':
            print("\nExiting... Goodbye!")
            break

        else:
            print("\n Invalid option. Choose 1, 2, or 3.")

if __name__ == "__main__":
    main()


