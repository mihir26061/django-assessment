# Django Assessment

## Setup Instructions

### 1. Clone repo
git clone <your-repo-url>
cd django-assessment

### 2. Create virtual env
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run migrations
python manage.py migrate

### 5. Run server
python manage.py runserver

---

## Celery Setup

### Start Redis (Docker)
docker run -d -p 6379:6379 redis

### Start Celery
celery -A django_assessment worker -l info -P solo

---

## Task 1
- Demonstrates N+1 query issue
- Optimized using select_related & prefetch_related

## Task 2
- Async job queue using Celery + Redis
- Rate limiting using Redis Sorted Set
- Retry with exponential backoff

## Task 3
- Multi-tenant isolation using custom manager & middleware

---

## Run Tests
pytest