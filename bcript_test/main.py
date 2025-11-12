import bcrypt
import os
import re

USER_DATA_FILE = "users.txt"

# Function 1: Hash Password
def hash_password(plain_text_password: str) -> str:
    """
    Hashes a plain text password using bcrypt and returns the hashed password.
    """
    password_bytes = plain_text_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")


# Function 2: Verify Password
def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a stored bcrypt hash.
    """
    password_bytes = plain_text_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)


# Function 3: Check if User Exists

def user_exists(username: str) -> bool:
    """
    Checks whether a given username already exists in the database.
    """
    if not os.path.exists(USER_DATA_FILE):
        return False

    with open(USER_DATA_FILE, "r") as f:
        next(f, None)  # Skip header
        for line in f:
            user, _, _ = line.strip().split(",", 2)
            if user == username:
                return True
    return False


# Function 4: Register User

def register_user(username: str, password: str, role: str = "user") -> bool:
    """
    Registers a new user by hashing their password and storing credentials.
    Returns True if successful, False if username already exists.
    """
    if user_exists(username):
        print(f"\nError: Username '{username}' already exists.")
        return False

    hashed_password = hash_password(password)

    # Ensure file exists and has a header
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "w") as f:
            f.write("username,password_hash,role\n")

    # Append new user credentials
    with open(USER_DATA_FILE, "a") as f:
        f.write(f"{username},{hashed_password},{role}\n")

    print(f"\n User '{username}' registered successfully with role '{role}'.")
    return True


# Function 5: Login User
def login_user(username: str, password: str) -> bool:
    """
    Authenticates a user by verifying their username and password.
    """
    if not os.path.exists(USER_DATA_FILE):
        print("\nNo users found. Please register first.")
        return False

    with open(USER_DATA_FILE, "r") as f:
        next(f, None)  # Skip header
        for line in f:
            user, stored_hash, role = line.strip().split(",", 2)
            if user == username:
                if verify_password(password, stored_hash):
                    print(f"\n Login successful. Welcome, {username} ({role}).")
                    return True
                else:
                    print("\n Incorrect password.")
                    return False

    print("\n Username not found.")
    return False


# Function 6: Validate Username

def validate_username(username: str) -> tuple:
    """
    Validates username format.
    """
    if not username:
        return False, "Username cannot be empty."
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if not re.match("^[A-Za-z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores."
    return True, ""



# Function 7: Validate Password

def validate_password(password: str) -> tuple:
    """
    Validates password strength.
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if not re.search("[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search("[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search("[0-9]", password):
        return False, "Password must contain at least one number."
    if not re.search("[@#$%^&+=!]", password):
        return False, "Password must contain at least one special character (@#$%^&+=!)."
    return True, ""


# Function 8: Display Menu

def display_menu():
    """Displays the main menu options."""
    print("\n" + "=" * 50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("=" * 50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-" * 50)


# Function 9: Main Program Loop

def main():
    """Main program loop."""
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == '1':
            # --- Registration Flow ---
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()

            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            password = input("Enter a password: ").strip()

            # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            role = input("Enter user role (e.g., admin, analyst, it_support): ").strip()

            # Attempt to register user
            if register_user(username, password, role):
                input("\nPress Enter to return to the main menu...")

        elif choice == '2':
            # --- Login Flow ---
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            if login_user(username, password):
                input("\nPress Enter to return to the main menu...")

        elif choice == '3':
            # --- Exit ---
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")


# Entry Point

if __name__ == "__main__":
    main()