# Week 7: Secure Authentication System

**Student Name:** Ayesha Noor 
**Student ID:** M01055122 
**Course:** CST1510 - CW2 - Multi-Domain Intelligence Platform  

---

##  Project Description

This project implements a **secure command-line authentication system** in Python.  
Users can **register accounts** and **log in securely**, with passwords hashed using `bcrypt`.  

The system demonstrates:
- Secure password storage and verification  
- User role management (e.g., user, admin, analyst)  
- Account security features like lockout after multiple failed attempts  
- Session token generation for logged-in users  
- File-based data persistence using `users.txt`, `sessions.json`, and `failed_attempts.json`

---

##  Features

-  **Secure Password Hashing** using `bcrypt` with automatic salting  
-  **User Registration** with role assignment  
-  **Password Strength Indicator** (Weak, Medium, Strong)  
-  **User Login** with hashed password verification  
-  **Account Lockout** after 3 failed login attempts (5 minutes)  
-  **Session Management** with unique session tokens  
-  **File-based Storage**:
  - `users.txt` → stores username, hashed password, and role  
  - `failed_attempts.json` → tracks failed login attempts for lockout  
  - `sessions.json` → stores active session tokens with timestamps  
- **Simple and clean CLI interface**  

---

##  Technical Implementation

| Component | Description |
|------------|-------------|
| **Language** | Python 3 |
| **Hashing Algorithm** | bcrypt with automatic salting |
| **Data Storage** | `users.txt`, `failed_attempts.json`, `sessions.json` |
| **Security** | One-way hashing, password never stored in plaintext |
| **Password Validation** | Strength evaluated based on length, uppercase/lowercase letters, digits, and special characters |
| **Account Lockout** | After 3 failed attempts, account locked for 5 minutes |
| **Session Management** | Unique session token generated after login using `secrets.token_hex` |

---
