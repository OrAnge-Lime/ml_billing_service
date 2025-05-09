import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

# for debug
import sys 
sys.path.append('/home/orange_lime/ITMO_projects/ml_billing_service/')

from router import router as asr_router
from config import asr_settings # Import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ASR service starting up...")
    logger.info(f"Using ASR Model Cache Directory: {asr_settings.MODEL_CACHE_DIRECTORY}")
    logger.info(f"Default device for models: {asr_settings.DEFAULT_DEVICE}")
    # Models are loaded lazily by the registry on first request
    yield
    logger.info("ASR service shutting down...")

app = FastAPI(
    title="ASR",
    description="Service for transcribing audio using OpenAI Whisper models.",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc", # Enable ReDoc
    lifespan=lifespan
)

# Basic error handler for unhandled exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception for request {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred."},
    )

app.include_router(asr_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8011, reload=True)