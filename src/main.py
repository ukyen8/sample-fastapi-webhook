import hashlib
import hmac
import http
import json
import os

from fastapi import FastAPI, Header, HTTPException, Request
from github import Github, GithubIntegration

app = FastAPI()

with open("private-key.pem") as fin:
    private_key = fin.read()

github_integration = GithubIntegration(os.environ.get("APP_ID"), private_key)


def generate_hash_signature(
    secret: bytes,
    payload: bytes,
    digest_method=hashlib.sha1,
):
    return hmac.new(secret, payload, digest_method).hexdigest()


def connect_repo(owner: str, repo_name: str):
    installation_id = github_integration.get_installation(owner, repo_name).id
    access_token = github_integration.get_access_token(installation_id).token
    connection = Github(login_or_token=access_token)
    return connection.get_repo(f"{owner}/{repo_name}")


@app.post("/webhook", status_code=http.HTTPStatus.ACCEPTED)
async def webhook(request: Request, x_hub_signature: str = Header(None)):
    payload = await request.body()
    secret = os.environ.get("WEBHOOK_SECRET").encode("utf-8")
    signature = generate_hash_signature(secret, payload)
    if x_hub_signature != f"sha1={signature}":
        raise HTTPException(status_code=401, detail="Authentication error.")

    payload_dict = json.loads(payload)
    if "repository" in payload_dict:
        owner = payload_dict["repository"]["owner"]["login"]
        repo_name = payload_dict["repository"]["name"]
        repo = connect_repo(owner, repo_name)
        if payload_dict.get("issue") and payload_dict["action"] == "opened":
            issue = repo.get_issue(number=payload_dict["issue"]["number"])
            issue.create_comment("Hello World!!!")
    return {}
