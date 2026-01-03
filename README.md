

## `README.md` for **Archgem_Framework** (Django backend)

# Archgem_Framework (Django backend)

Backend framework for the Archgem iOS client. Provides:
- Session initialization (CSRF token bootstrap)
- Login endpoint (Django session + DRF token)
- Landmark (“Gem”) search endpoint

## Tech stack
- Python + Django
- Django REST Framework (Token model used)
- Default DB in repo: SQLite (`db.sqlite3`)

## Apps
- `Login`: authentication endpoint at `/Login/`
- `Home`: gem search endpoint at `/Home/Search/`
- Project module: `Archgem`

## Data model: Gem
`Home.models.Gem` fields include:
- `uid` (UUID, primary key)
- `name`, `latitude`, `longitude`
- optional metadata: address/city/country/description/architect/style/years/image_url/website/type

DB table: `gem_locations`
Uniqueness constraint: `(latitude, longitude)`

## API endpoints

### `GET /`
Session initialization.
- Returns JSON: `{ "SID": <int>, "CSRF": "<token>" }`
- Intended to prime CSRF and session behavior for the iOS client.

### `POST /Login/`
Login or token validation.
- Login with credentials:
  - Body: `{ "username": "...", "password": "..." }`
  - On success: logs in user (session cookie) and returns `{ "token": "<drf_token>" }`
- Validate existing token:
  - Body: `{ "token": "<drf_token>" }`
  - On success: logs in user (session cookie) and returns `{ "token": "<drf_token>" }`

### `POST /Home/Search/`
Gem search. Requires authenticated Django session.
- Body (all optional, defaults used if omitted):
  - `centerLat`, `centerLong`
  - `spanDeltaLat`, `spanDeltaLong`
  - `startsWith` (string)
- Response:
  - `{ "gems": [ { id, name, lat, long, ... } ] }`

## Local development setup

TODO
