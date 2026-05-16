# AI Emoji Maker - API Endpoints Documentation

This document provides complete details for all REST API endpoints exposed by the AI Emoji Maker FastAPI backend.

---

## Base URL
All API requests (except the root health check) are prefixed with `/api`.
When running locally: `http://localhost:8000`

---

## 1. System Health

### `GET /`
Verifies server health, environment mode, and database connectivity.

- **Auth Required**: No
- **Headers**: None
- **Response** (`200 OK`):
```json
{
  "status": "healthy",
  "service": "AI Emoji Maker API",
  "environment": "development",
  "aimlapi_model": "flux/schnell",
  "supabase_connected": true
}
```

#### Example `curl`:
```bash
curl -X GET http://localhost:8000/
```

---

## 2. Authentication

### `POST /api/auth/signup`
Registers a new user account via Supabase Auth and automatically creates an application profile record in the `profiles` table.

- **Auth Required**: No
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "email": "alex.patel@acmecorp.com",
  "password": "securepassword123",
  "first_name": "Alex",
  "last_name": "Patel"
}
```
- **Response** (`201 Created`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "email": "alex.patel@acmecorp.com",
    "first_name": "Alex",
    "last_name": "Patel"
  }
}
```

#### Example `curl`:
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "alex@example.com", "password": "supersecret123", "first_name": "Alex", "last_name": "Patel"}'
```

---

### `POST /api/auth/login`
Authenticates an existing user and returns a JSON Web Token (JWT) for secure API requests.

- **Auth Required**: No
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "email": "alex.patel@acmecorp.com",
  "password": "securepassword123"
}
```
- **Response** (`200 OK`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "email": "alex.patel@acmecorp.com",
    "first_name": "Alex",
    "last_name": "Patel"
  }
}
```

#### Example `curl`:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alex@example.com", "password": "supersecret123"}'
```

---

### `POST /api/auth/token`
OAuth2 password request form endpoint required for interactive Swagger UI login (`http://localhost:8000/docs`).

- **Auth Required**: No
- **Headers**: `Content-Type: application/x-www-form-urlencoded`
- **Form Data**: `username=alex@example.com&password=supersecret123`
- **Response** (`200 OK`): Same structure as `/api/auth/login`.

---

## 3. Emoji Generation

### `POST /api/emoji/generate`
Generates a custom workplace reaction or sticker using FLUX.1 Schnell via AIMLAPI. Automatically records generation metadata in the `image_generations` table and increments the user's `generations_used` counter.

- **Auth Required**: Yes (`Bearer <JWT_TOKEN>`)
- **Headers**: 
  - `Authorization: Bearer <YOUR_ACCESS_TOKEN>`
  - `Content-Type: application/json`
- **Request Body**:
  - `prompt` (string, required): Raw user description.
  - `style` (string, optional): Visual style (`Sticker`, `Flat`, `Doodle`, `Pixel`, `Mascot`). Default: `Sticker`.
  - `mood` (string, optional): Emotional tone (`Happy`, `Tired`, `Confused`, `Celebrate`). Default: `Happy`.
  - `width` (int, optional): Pixel width (must be multiple of 32, e.g., `64`, `128`, `256`). Default: `128`.
  - `height` (int, optional): Pixel height (must be multiple of 32, e.g., `64`, `128`, `256`). Default: `128`.

```json
{
  "prompt": "celebrating squashing a production bug",
  "style": "Sticker",
  "mood": "Celebrate",
  "width": 128,
  "height": 128
}
```

- **Response** (`200 OK`):
```json
{
  "id": "gen-1715865000",
  "user_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "original_prompt": "celebrating squashing a production bug",
  "final_prompt": "A high quality workplace reaction emoji. vibrant die-cut vinyl sticker with a distinct crisp white border contour. Subject: celebrating squashing a production bug. Mood/Expression: Celebrate. Single centered object, perfectly isolated on a solid pristine white background, perfectly square composition, professional workplace chat reaction icon, flawless details.",
  "image_url": "https://api.aimlapi.com/images/...",
  "image_size": "128x128",
  "style": "Sticker",
  "mood": "Celebrate",
  "created_at": "2026-05-16T14:30:00Z"
}
```

#### Example `curl`:
```bash
curl -X POST http://localhost:8000/api/emoji/generate \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "coffee urgency before morning standup", "style": "Sticker", "mood": "Tired", "width": 128, "height": 128}'
```

---

### `GET /api/emoji/history`
Retrieves all past emoji generations for the authenticated user, ordered by creation date descending.

- **Auth Required**: Yes (`Bearer <JWT_TOKEN>`)
- **Headers**: `Authorization: Bearer <YOUR_ACCESS_TOKEN>`
- **Response** (`200 OK`):
```json
{
  "generations": [
    {
      "id": "gen-1715865000",
      "user_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
      "original_prompt": "celebrating squashing a production bug",
      "final_prompt": "A high quality workplace reaction emoji...",
      "image_url": "https://api.aimlapi.com/images/...",
      "image_size": "128x128",
      "style": "Sticker",
      "mood": "Celebrate",
      "created_at": "2026-05-16T14:30:00Z"
    }
  ]
}
```

#### Example `curl`:
```bash
curl -X GET http://localhost:8000/api/emoji/history \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

---

## 4. Error Responses
All API error responses adhere to standard HTTP status codes and provide a clear JSON error structure:

```json
{
  "detail": "Error description message"
}
```

### Common Status Codes:
- `400 Bad Request`: Validation failure or duplicate email registration.
- `401 Unauthorized`: Missing, invalid, or expired JWT bearer token.
- `422 Unprocessable Entity`: Invalid request schema (e.g., width/height not within limits).
- `502 Bad Gateway` / `504 Gateway Timeout`: Upstream error communicating with AIMLAPI image provider.
