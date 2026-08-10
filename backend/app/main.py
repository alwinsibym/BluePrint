from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME
)

# Enable CORS for all origins (local network IPs, localhost, custom ports)
# NOTE: allow_credentials=True is NOT compatible with allow_origins=["*"].
# Since this API uses no cookies or credential-bearing headers, we leave it False.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length"],
)


# Include the router at the root so that /generate is available directly
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"status": "running", "project": settings.PROJECT_NAME}
