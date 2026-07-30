from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME
)

# Enable CORS for all origins (local network IPs, localhost, custom ports)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router at the root so that /generate is available directly
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"status": "running", "project": settings.PROJECT_NAME}
