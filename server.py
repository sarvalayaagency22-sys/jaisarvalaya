from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone
from contextlib import asynccontextmanager

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FIX: MongoDB client and db moved inside lifespan so the connection is
# properly opened and closed with the application lifecycle, preventing leaks.
client = None
db = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'jaisarvalaya')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    logger.info("Starting up Jai Sarvalaya API...")
    yield
    logger.info("Shutting down — closing MongoDB connection.")
    client.close()

# Create the main app
app = FastAPI(title="Jai Sarvalaya API", lifespan=lifespan)

# FIX: CORS credentials + wildcard origin is forbidden by the CORS spec and
# Starlette raises a ValueError at startup when both are set simultaneously.
# Read explicit origins from the env var; fall back to localhost for safety.
# If you need to allow all origins in development, set allow_credentials=False.
_raw_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000')
_allow_origins = [o.strip() for o in _raw_origins.split(',') if o.strip()]
_allow_credentials = '*' not in _allow_origins  # credentials only when origins are explicit

app.add_middleware(
    CORSMiddleware,
    allow_credentials=_allow_credentials,
    allow_origins=_allow_origins if _allow_credentials else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# --- Models ---
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


# --- Routes ---
@api_router.get("/")
async def root():
    return {"message": "Jai Sarvalaya API is running!"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)

    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()

    await db.status_checks.insert_one(doc)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)

    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])

    return status_checks


# Include router
app.include_router(api_router)

