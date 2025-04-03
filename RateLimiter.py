from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
import time
import json

app = FastAPI()

# Load request log from file
try:
    with open("state.json", "r") as syakir_file:
        request_log = json.load(syakir_file)
except FileNotFoundError:
    request_log = {}

# Config
ENDPOINT = "/limited"
RATE_LIMIT = 4

@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    ip = request.client.host
    now = time.time()
    key = f"{ip}:{request.url.path}"

    logs = request_log.get(key, [])
    logs = [timestamp for timestamp in logs if now - timestamp < 1]

    if request.url.path == ENDPOINT and len(logs) >= RATE_LIMIT:
        print(f"LIMITED: {ip} hit the limit ({len(logs)} reqs/sec)")
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})

    logs.append(now)
    request_log[key] = logs

    if request.url.path == ENDPOINT:
        print(f"ALLOWED: {ip} → {len(logs)} request in 1s")

    with open("state.json", "w") as syakir_file:
        json.dump(request_log, syakir_file)

    response = await call_next(request)
    return response

@app.get("/")
def home():
    return {"message": "Rate limits user request"}

@app.get(ENDPOINT)
def limited():
    return {"message": "Request allowed"}