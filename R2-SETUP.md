# AxelPath — Cloudflare R2 setup

1. Create an R2 bucket named `axelpath` (or another name).
2. Create an R2 API token with object read/write permissions for this bucket.
3. Put credentials only in `backend/.env`.
4. Set `R2_ENABLED=true`.
5. Restart the backend.

Example:

```env
R2_ENABLED=true
R2_ENDPOINT_URL=https://YOUR_ACCOUNT_ID.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=YOUR_ACCESS_KEY
R2_SECRET_ACCESS_KEY=YOUR_SECRET_KEY
R2_BUCKET_NAME=axelpath
R2_REGION=auto
R2_SIGNED_URL_EXPIRE_SECONDS=900
```

Students and the frontend never receive R2 credentials.
