# Quiz Master

A quiz platform for exam preparation and assessment management.

## Features

- JWT Authentication
- Role-based Access Control
- Real-time Analytics
- Mobile Responsive Design
- Redis Caching
- Background Tasks
- CSV Export
- Email Notifications

## Tech Stack

Frontend:
- Vue.js 3
- Pinia
- Tailwind CSS
- Chart.js

Backend:
- Flask
- SQLAlchemy
- Celery
- Redis
- PostgreSQL

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kapilovsky/MAD-2-Kwizzy.git
cd quiz_master_21f1006340
```

2. Backend Setup:
```bash
cd server
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Frontend Setup:
```bash
cd ../client
npm install
```

4. Run the application:
```bash
cd server
flask run

cd client
npm run dev

cd server
celery -A celery_worker.celery worker --loglevel=info

cd server
celery -A celery_worker.celery beat --loglevel=info
```

## Documentation

- [API Documentation](docs/api.md)
- [Database Schema](docs/schema.md)
- [Deployment Guide](docs/deployment.md)

## License

MIT License 