# **Vehicle Parking Management System**

A comprehensive web application for managing vehicle parking spaces, reservations, and user accounts.

**Technology Stack**

**Core Technologies**

* **Python 3.x** – Primary scripting language powering backend logic
* **SQLite** – Lightweight embedded database ideal for development; adaptable to other relational engines if needed

**Web Framework**

* **Flask** – Minimalistic Python web framework
	+ Acts as the core for request routing and response handling
	+ Supports modular design via Blueprint components

**Database**

* **SQLAlchemy** – Object-relational mapper for Python
	+ Facilitates intuitive data access via Python classes
	+ Promotes DB-agnostic coding practices
* **Flask-SQLAlchemy** – Integration layer between Flask and SQLAlchemy
	+ Simplifies database sessions
	+ Manages connections efficiently within the Flask app context

**User Authentication & Security**

* **Flask-Login** – User session and login state handler
	+ Tracks active users across requests
	+ Supports persistent sessions with loader functions
* **Werkzeug Security** – Utility for safe password storage
	+ Offers tools for password hashing and verification
	+ Enhances request security through middleware
* **email-validator** – Validates user email formats
	+ Ensures submitted email strings conform to accepted standards

**Web Forms**

* **Flask-WTF** – Secure and validated form management
	+ Brings WTForms support to Flask apps
	+ Offers CSRF protection and built-in form validation utilities

 **Database Structure**
 please check ER-Diagram.png for the database structure

 **Project Structure**
 please check project_structure.png for the project structure