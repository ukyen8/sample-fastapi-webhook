import hashlib
import hmac
import http
import os

from fastapi import FastAPI, Header, HTTPException, Request

app = FastAPI()


def generate_hash_signature(
    secret: bytes,
    payload: bytes,
    digest_method=hashlib.sha1,
):
    return hmac.new(secret, payload, digest_method).hexdigest()


@app.post("/webhook", status_code=http.HTTPStatus.ACCEPTED)
async def webhook(request: Request, x_hub_signature: str = Header(None)):
    payload = await request.body()
    secret = os.environ.get("WEBHOOK_SECRET").encode("utf-8")
    signature = generate_hash_signature(secret, payload)
    if x_hub_signature != f"sha1={signature}":
        raise HTTPException(status_code=401, detail="Authentication error.")
    return {}
