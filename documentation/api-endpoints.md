# AI Emoji Maker — API Reference

**Base URL (local):** `http://localhost:8000`  
All endpoints (except the health check) are prefixed with `/api`.  
Authenticated endpoints require: `Authorization: Bearer <JWT_TOKEN>`

---

## 1. Health Check

### `GET /`
Returns server status, environment, and database connectivity.

**Auth:** None

**Response `200`:**
```json
{
  "status": "healthy",
  "service": "AI Emoji Maker API",
  "environment": "development",
  "aimlapi_model": "flux/schnell",
  "supabase_connected": true
}
```
```bash
curl http://localhost:8000/
```

---

## 2. Authentication

### `POST /api/auth/signup`
Registers a new user and creates their profile in the `profiles` table.

**Auth:** None | **Content-Type:** `application/json`

**Request:**
```json
{
  "email": "alex@example.com",
  "password": "supersecret123",
  "first_name": "Alex",
  "last_name": "Patel"
}
```

**Response `201`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    "email": "alex@example.com",
    "first_name": "Alex",
    "last_name": "Patel"
  }
}
```
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"alex@example.com","password":"supersecret123","first_name":"Alex","last_name":"Patel"}'
```

---

### `POST /api/auth/login`
Authenticates a user and returns a JWT.

**Auth:** None | **Content-Type:** `application/json`

**Request:**
```json
{
  "email": "alex@example.com",
  "password": "supersecret123"
}
```

**Response `200`:** Same structure as `/api/auth/signup`.

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alex@example.com","password":"supersecret123"}'
```

---

### `POST /api/auth/token`
OAuth2 password form endpoint — used by Swagger UI (`/docs`) for interactive login.

**Auth:** None | **Content-Type:** `application/x-www-form-urlencoded`  
**Form fields:** `username`, `password`  
**Response `200`:** Same structure as `/api/auth/login`.

---

## 3. User Profile

### `GET /api/users/me`
Returns the full profile for the currently authenticated user, including their plan and generation usage.

**Auth:** Required

**Response `200`:**
```json
{
  "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "email": "alex@example.com",
  "first_name": "Alex",
  "last_name": "Patel",
  "plan_type": "Free",
  "generations_used": 3,
  "max_generations": 10
}
```

> `max_generations` is computed from `plan_type` — not stored in the database.
>
> | Plan    | Max Generations |
> |---------|-----------------|
> | Free    | 10              |
> | Premium | 100             |
> | Ultra   | 500             |

```bash
curl http://localhost:8000/api/users/me \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

---

## 4. Emoji Generation

### `POST /api/emoji/generate`
Generates an emoji/sticker image using FLUX.1 Schnell (via AIMLAPI). Records generation metadata and increments the user's `generations_used` counter.

**Auth:** Required | **Content-Type:** `application/json`

**Request fields:**

| Field    | Type   | Required | Default   | Notes |
|----------|--------|----------|-----------|-------|
| `prompt` | string | ✅       | —         | Raw description of the emoji |
| `style`  | string | ❌       | `Sticker` | `Sticker`, `Flat`, `Doodle`, `Pixel`, `Mascot` |
| `mood`   | string | ❌       | `Happy`   | `Happy`, `Tired`, `Confused`, `Celebrate` |
| `width`  | int    | ❌       | `128`     | Must be a multiple of 32 |
| `height` | int    | ❌       | `128`     | Must be a multiple of 32 |

**Request:**
```json
{
  "prompt": "celebrating squashing a production bug",
  "style": "Sticker",
  "mood": "Celebrate",
  "width": 128,
  "height": 128
}
```

**Response `200`:**
```json
{
  "id": "gen-1715865000",
  "user_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "original_prompt": "celebrating squashing a production bug",
  "final_prompt": "A high quality workplace reaction emoji. vibrant die-cut vinyl sticker...",
  "image_url": "https://api.aimlapi.com/images/...",
  "image_size": "128x128",
  "style": "Sticker",
  "mood": "Celebrate",
  "created_at": "2026-05-16T14:30:00Z"
}
```
```bash
curl -X POST http://localhost:8000/api/emoji/generate \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"coffee urgency before morning standup","style":"Sticker","mood":"Tired","width":128,"height":128}'
```

---

### `GET /api/emoji/history`
Returns all past emoji generations for the authenticated user, newest first.

**Auth:** Required

**Response `200`:**
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
```bash
curl http://localhost:8000/api/emoji/history \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

---

## 5. Error Responses

All errors return a standard JSON body:
```json
{ "detail": "Error description message" }
```

| Status | Meaning |
|--------|---------|
| `400`  | Validation failure or duplicate email |
| `401`  | Missing, invalid, or expired JWT |
| `404`  | Resource not found (e.g., user profile) |
| `422`  | Invalid request schema (e.g., width/height not a multiple of 32) |
| `502` / `504` | Upstream AIMLAPI error or timeout |
