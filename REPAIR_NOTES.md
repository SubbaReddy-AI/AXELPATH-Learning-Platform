# AXELPATH repair notes

- Added the supplied AXELPATH logo at `frontend/public/axelpath-logo.png`.
- Removed the public administrator signup option. Admin accounts are created from backend environment settings.
- Kept student signup enabled.
- Added `VITE_BACKEND_PROXY` support to the Vite development proxy.
- The Docker frontend proxies `/api` to the backend service through nginx.

## Run

```powershell
docker compose down
docker compose up --build -d
docker compose ps
```

Open `http://localhost:3000` or `http://YOUR-LAN-IP:3000`.
