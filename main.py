import bcrypt
import os

# Function 1: Hash a Password
def hash_password(plain_text_password: str) -> str:
    """
    Hashes a plain text password using bcrypt and returns the hashed password.
    """
    password_bytes = plain_text_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password.decode("utf-8")

# Function 2: Verify a Password
def verify_password(plain_text_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a hashed password.
    """
    password_bytes = plain_text_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

# Function 3: Register a New User
def register_user(username: str, password: str, role: str = "user") -> None:
    """
    Registers a new user by hashing their password and saving to users.txt.
    """
    hashed_password = hash_password(password)

    # Ensure users.txt exists
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f:
            f.write("username,password_hash,role\n")

    # Append new user credentials
    with open("users.txt", "a") as f:
        f.write(f"{username},{hashed_password},{role}\n")

    print(f" User '{username}' registered successfully with role '{role}'.")

# Function 4: Login Existing User
def login_user(username: str, password: str) -> bool:
    """
    Logs in a user by verifying the entered password against the stored hash.
    """
    if not os.path.exists("users.txt"):
        print(" No users found. Please register first.")
        return False

    with open("users.txt", "r") as f:
        next(f) 
        for line in f:
            user, stored_hash, role = line.strip().split(",", 2)
            if user == username:
                if verify_password(password, stored_hash):
                    print(f" Login successful. Welcome, {username} ({role}).")
                    return True
                else:
                    print(" Incorrect password.")
                    return False

    print(" Username not found.")
    return False

# Main Function (Command-Line Interface)
def main():
    """
    Command-line menu for registering and logging in users.
    """
    print("\n=== Multi-Domain Intelligence Platform: Secure Login ===")
    print("1. Register a new user")
    print("2. Log in")
    choice = input("Select an option (1 or 2): ")

    if choice == "1":
        username = input("Enter new username: ").strip()
        password = input("Enter new password: ").strip()
        role = input("Enter role (e.g., analyst, admin, it_support): ").strip()
        register_user(username, password, role)

    elif choice == "2":
        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()
        login_user(username, password)

    else:
        print(" Invalid option. Please select 1 or 2.")

# Run Program
if __name__ == "__main__":
    main()