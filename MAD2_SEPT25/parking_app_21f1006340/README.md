Project Title: **MAD 2 Vehicle Parking App**

Problem Statement:
To design and build a web-based application that has both backend and frontend functionalities for a Vehicle Parking System, assisting both Users and Admin.

Approach:
I built the app using flask for backend and vue for front end, while using sqlalchemy for database modeling. I also used redis for server caching and celery for backend scheduled jobs.

**Technologies and Frameworks Used**

Technology / Library | Purpose
--------------------|--------
Flask | Backend code work
SQLAlchemy | ORM for database
VueJS | Frontend UI
Bootstrap 5 | Frontend styling
Chart.js | Frontend charts
Redis | Caching
Celery | Backend scheduled jobs
SQLite | Storing user data

**Database Schema / ER Diagram**

Tables:

Users — for user details (id, name, email, password)
Admins— for admin details (id, password, username)
Parking Lots— for parking lots (id, address, max no. of spots, price)
Parking Spots— for parking spots inside lots (id, address, max no. of spots, price)
Reservations— for user reservations (id, leaving time, parking time, spot id, user id)
