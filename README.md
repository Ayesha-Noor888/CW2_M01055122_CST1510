Project for module CST1510
# Week 7: Secure Authentication System

**Student Name:** Ayesha Noor  
**Student ID:** M01055122  
**Course:** CST1510 - CW2 - Multi-Domain Intelligence Platform  

---

## Project Description

This project implements a **secure authentication system** using the Python programming language.  
The system allows users to **register new accounts** and **log in securely** using password hashing through the `bcrypt` library.  
All user information, including usernames and hashed passwords, is stored persistently in a file named `users.txt`.  

This project demonstrates an understanding of:
- File handling in Python  
- Password hashing for security  
- Logical flow control  
- Clean and well-structured Python programming practices  

---

## Features

-  Secure password hashing using **bcrypt** with automatic salt generation  
-  User registration that stores username, hashed password, and role in a file  
-  User login verification against hashed passwords  
-  File-based persistence using `users.txt`  
-  Clear feedback for successful registration or login attempts  
-  Modular code structure with separate, reusable functions  

---

## Technical Implementation

| Component | Description |
|------------|-------------|
| **Language** | Python 3 |
| **Hashing Algorithm** | bcrypt with automatic salting |
| **Data Storage** | Plain text file (`users.txt`) with comma-separated values |
| **Security** | One-way hashing ensures no plaintext passwords are stored |
| **Libraries Used** | `bcrypt`, `os` |
| **Program Entry Point** | `main()` function with simple text-based interface |
