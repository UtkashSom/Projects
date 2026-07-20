# Quiz Master App

A web application built with Flask and VueJS for creating and taking quizzes. This project is part of the MAD 1 course assignment.

## Features
- Quiz creation and management
- Multiple choice questions
- User authentication
- Score tracking
- Interactive UI with VueJS

## Tech Stack
- Backend: Flask (Python)
- Frontend: VueJS
- Database: SQLite
- ORM: SQLAlchemy

## Setup Instructions
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python run.py
   ```

## Project Structure
```
quiz_master_app/
├── backend/             # Flask application
│   ├── models/         # Database models
│   ├── routes/         # API routes
│   └── config.py       # Configuration
├── frontend/           # VueJS application
│   ├── src/           # Source files
│   └── public/        # Static files
└── requirements.txt    # Python dependencies
```

## Contributing
This is a private repository for MAD 1 course assignment. Collaborators:
- MADII-cs2006

## License
This project is part of the MAD 1 course assignment.