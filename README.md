# CourseDrive - Modern E-Learning & Course Platform

CourseDrive is a full-featured Coursera-like online course platform built with FastAPI, PostgreSQL, Redis, SQLAlchemy 2.0, Stripe, Cloudinary, and Next.js 14.

## Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **ORM & Database:** SQLAlchemy 2.0 (asyncio) + PostgreSQL (`asyncpg`) + Alembic
- **Caching & OTP:** Redis (`aioredis` / `redis-py`)
- **Authentication:** JWT (Access & Refresh Tokens) + Passlib/Bcrypt
- **Payment Processing:** Stripe Checkout & Webhooks
- **Media & File Storage:** Cloudinary & Local File Fallback
- **PDF Certificates:** ReportLab
- **Email:** AIO-SMTP / Template mailing

### Frontend
- **Framework:** Next.js 14 (App Router) + TypeScript
- **Styling:** Tailwind CSS + Radix UI / shadcn/ui
- **Forms & Validation:** React Hook Form + Zod
- **Video & Media:** Video.js / HLS / Custom Player

---

## Getting Started

### 1. Start Infrastructure (PostgreSQL & Redis)
```bash
docker-compose up -d
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

# Run Alembic migrations (or allow auto-creation)
alembic upgrade head

# Start API Server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).
