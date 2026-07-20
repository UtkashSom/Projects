# Quiz Master V2

A multi-user quiz application built with Flask and Vue.js for exam preparation.

## Features

- Multi-user system with Admin and User roles
- Subject and Chapter management
- Quiz creation and management
- User quiz attempts and scoring
- Daily reminders
- Monthly activity reports
- CSV export functionality
- Redis caching
- Celery for background jobs

## Tech Stack

- Backend: Flask
- Frontend: Vue.js
- Database: SQLite
- Caching: Redis
- Background Jobs: Celery
- Styling: Bootstrap

## Project Structure

```
quiz_master_21f1006340/
├── backend/           # Flask application
│   ├── app/
│   ├── config/
│   └── requirements.txt
├── frontend/         # Vue.js application
│   ├── src/
│   └── package.json
└── README.md
```

## Setup Instructions

1. Clone the repository
2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```
4. Run the application:
   ```bash
   # Terminal 1 - Backend
   cd backend
   flask run
   
   # Terminal 2 - Frontend
   cd frontend
   npm run serve
   ```

## Development Status

- [x] Repository Setup
- [ ] Backend Setup
- [ ] Frontend Setup
- [ ] Database Models
- [ ] API Endpoints
- [ ] User Interface
- [ ] Testing
- [ ] Documentation 