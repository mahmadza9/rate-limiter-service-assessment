from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
import time
import json

# Use FastAPI web framework
app = FastAPI()

# Load request log file
try:
    with open("state.json", "r") as syakir_file:
        request_log = json.load(syakir_file)
except FileNotFoundError:
    request_log = {}

# API path that will be rate-limited and number of request allowed
ENDPOINT = "/limited"
RATE_LIMIT = 4

# Use middleware to implement rate limiting
@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    ip = request.client.host
    now = time.time()
    key = f"{ip}:{request.url.path}"

    logs = request_log.get(key, [])
    logs = [timestamp for timestamp in logs if now - timestamp < 1]

    # If the request reach limited endpoint and the number of requests exceeds the limit,
    # Deny the request with "429 Too Many Requests response"
    if request.url.path == ENDPOINT and len(logs) >= RATE_LIMIT:
        print(f"LIMITED: {ip} hit the limit ({len(logs)} reqs/sec)")
        return JSONResponse(status_code=429, content={"detail": "Getting too many requests"})

    logs.append(now)
    request_log[key] = logs

    if request.url.path == ENDPOINT:
        print(f"ALLOWED: {ip} → {len(logs)} request in 1s")

    with open("state.json", "w") as syakir_file:
        json.dump(request_log, syakir_file)

    response = await call_next(request)
    return response

# Defines the root endpoint "/" which to show message
@app.get("/")
def home():
    return {"message": "Hello! This is a rate limiter service"}

# Defines the "/limited" endpoint for rate limiting.
@app.get(ENDPOINT)
def limited():
    return {"message": "Request allowed"}