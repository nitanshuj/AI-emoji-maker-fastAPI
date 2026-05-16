# AI Emoji Maker - Production FastAPI Backend

A simple but robust, production-ready FastAPI backend designed to power the AI Emoji Maker web application. It integrates **Supabase Auth** for secure user management, **Supabase Database** for storing generation metadata, and **AIMLAPI** (FLUX.1 Schnell) for blazing fast, high-quality emoji & sticker generation.

---

## Features

- **Supabase Authentication**: Complete endpoints for user registration (`POST /api/auth/signup`) and login (`POST /api/auth/login`), backed by secure JWT verification dependencies.
- **AIMLAPI FLUX.1 Schnell Integration**: Optimized prompt enhancement to transform user input into vibrant sticker-style vector graphics.
- **Strict Size Constraints & Cost Optimization**: Automatically enforces valid image dimensions (multiples of 32, e.g. 64x64, 128x128, 256x256) as required by AIMLAPI's FLUX models to optimize generation latency and cost.
- **Supabase Metadata Persistence**: Automatically records every generated reaction, storing prompt details, art style, mood, image URLs, and timestamps.
- **Development/Mock Fallback Mode**: Gracefully simulates generation and authentication when running locally without active API keys so frontend development is never blocked.

---

## Project Structure

```
AI-emoji-maker-fastAPI/
├── app/
│   ├── __init__.py
│   ├── main.py                # Application entrypoint & CORS setup
│   ├── config.py              # Environment & secrets management (pydantic-settings)
│   ├── schemas/               # Request & response data models
│   │   ├── auth.py
│   │   └── emoji.py
│   ├── services/              # External provider integrations
│   │   ├── aiml_service.py    # FLUX.1 image generation client
│   │   └── supabase_service.py # Database persistence layer
│   └── api/
│       ├── deps.py            # Authentication & JWT verification middleware
│       └── routes/
│           ├── auth.py        # /api/auth endpoints
│           └── emoji.py       # /api/emoji endpoints
├── .env.example               # Template for environment variables
├── requirements.txt           # Production package dependencies
└── schema.sql                 # Supabase SQL DDL for database setup
```

---

## Setup & Installation

### 1. Database Setup (Supabase)

1. Create a new project in your [Supabase Dashboard](https://supabase.com).
2. Open the **SQL Editor** in Supabase and paste the entire contents of `schema.sql`.
3. Run the script to create the `emoji_generations` table and associated indexes.

### 2. Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Fill in your credentials:
   - `SUPABASE_URL`: Your Supabase project URL.
   - `SUPABASE_ANON_KEY`: Your Supabase API anon key.
   - `AIMLAPI_API_KEY`: Your API key from [AIMLAPI](https://aimlapi.com/).

### 3. Running Locally

1. Install dependencies (virtual environment recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
3. Interactive Swagger API documentation is available at `http://localhost:8000/docs`.

---

## API Endpoints & Example Requests

### 1. System Health Check
```bash
curl -X GET http://localhost:8000/
```

### 2. User Sign Up
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword123", "name": "Creative Professional"}'
```

### 3. User Sign In (Get JWT Token)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword123"}'
```

### 4. Generate Emoji Reaction (Authenticated)
```bash
# Replace <YOUR_ACCESS_TOKEN> with the token obtained from login
curl -X POST http://localhost:8000/api/emoji/generate \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "celebrating squashing a production bug", "style": "Sticker", "mood": "Celebrate", "width": 128, "height": 128}'
```

### 5. Fetch Generation History (Authenticated)
```bash
curl -X GET http://localhost:8000/api/emoji/history \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```