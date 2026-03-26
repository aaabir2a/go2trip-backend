# Go2Trip Backend — Setup Guide

## Prerequisites
- Python 3.11+
- PostgreSQL 15+
- pip

## 1. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

## 2. Install dependencies
```bash
pip install -r requirements.txt
```

## 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials and secret key
```

## 4. Create PostgreSQL database
```sql
CREATE DATABASE go2trip_db;
```

## 5. Run migrations
```bash
python manage.py makemigrations authentication destinations tours availability bookings reviews blogs
python manage.py migrate
```

## 6. Create superuser (admin)
```bash
python manage.py createsuperuser
```

## 7. Run development server
```bash
python manage.py runserver
```

API available at: http://localhost:8000/api/v1/
Swagger docs: http://localhost:8000/api/docs/

## API Endpoints Summary
| Endpoint | Methods | Auth |
|---|---|---|
| /api/v1/auth/register/ | POST | Public |
| /api/v1/auth/login/ | POST | Public |
| /api/v1/auth/logout/ | POST | JWT |
| /api/v1/auth/profile/ | GET, PATCH | JWT |
| /api/v1/auth/users/ | GET | Admin |
| /api/v1/destinations/ | GET, POST, PATCH, DELETE | Read-public, Write-admin |
| /api/v1/tours/ | GET, POST, PATCH, DELETE | Read-public, Write-admin |
| /api/v1/availability/{slug}/ | GET | Public |
| /api/v1/availability/schedules/ | CRUD | Admin |
| /api/v1/bookings/ | GET, POST | JWT |
| /api/v1/bookings/{id}/cancel/ | POST | JWT (owner/admin) |
| /api/v1/bookings/{id}/update-status/ | POST | Admin |
| /api/v1/reviews/ | GET, POST | Read-public, Write-JWT |
| /api/v1/blogs/ | GET, POST, PATCH, DELETE | Read-public, Write-admin |
