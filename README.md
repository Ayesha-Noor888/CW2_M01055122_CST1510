📊 Multi-Domain Intelligence Platform

CST1510 – Software Development | Streamlit Project

📌 Project Overview

The Multi-Domain Intelligence Platform is a Streamlit-based web application designed to analyse and manage information across three real-world IT domains:

🛡️ Cybersecurity Incidents

📂 Datasets & Metadata

🎫 IT Support Tickets

The platform provides interactive dashboards, database-driven operations, and an AI assistant to support analysis and decision-making. The project was developed incrementally over multiple weeks, with a strong focus on Object-Oriented Programming (OOP) and clean software architecture.

🏗️ System Architecture & Code Organization

The project follows a layered OOP architecture, separating responsibilities clearly:

multi_domain_platform/
│── models/        # Core entity classes (User, Dataset, Ticket, Incident)
│── services/      # Business logic & database services
│── database/      # SQLite database files
│── pages/         # Streamlit UI pages (dashboards)
│── app.py         # Main entry point (home page)
│── README.md

Key Classes

User – authentication and role handling

SecurityIncident – cyber incident representation

Dataset – dataset metadata and calculations

ITTicket – IT support ticket lifecycle

DatabaseManager – handles all database access

AuthManager – login & registration logic

This refactoring (Week 11) removed raw SQL from Streamlit pages and improved maintainability, readability, and scalability.

📊 Key Features
🛡️ Cyber Incidents Dashboard

View incidents by severity and status

Visualise trends using bar charts

Helps identify high-risk security threats

📂 Datasets Dashboard

Manage dataset metadata (CRUD)

Analyse record counts and file sizes

Interactive charts using Plotly

🎫 IT Tickets Dashboard

Create and manage IT support tickets

Track ticket priority and resolution status

Supports operational efficiency

🤖 AI Assistant (Gemini / ChatGPT)

Integrated AI assistant for explanations and guidance

Supports users when analysing incidents or tickets

Gracefully handles API quota limitations

🎨 User Interface

Built using Streamlit

Clear navigation via sidebar

Informational banners for usability

Enhanced home page with professional welcome layout

🛠️ Technologies Used

Python 3

Streamlit

SQLite

Plotly

Object-Oriented Programming (OOP)

Git & GitHub
