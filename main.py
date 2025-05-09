import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

# Routers
from infrastructure.web.controllers import user_controller, model_controller, prediction_controller
from infrastructure.web.dependencies.use_cases import get_model_use_case
from infrastructure.db.database import create_tables
# Import the module directly to set its global variable
from infrastructure.web.dependencies import ml_model as http_client_module
from config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Main Billing API starting up...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"ASR Service URL: {settings.ASR_SERVICE_URL}")

    await create_tables()
    logger.info("Database tables checked/created.")
    yield

    logger.info("Main Billing API shutting down...")
    if http_client_module._asr_http_client_instance:
        logger.info("Closing ASR HTTP client...")
        await http_client_module._asr_http_client_instance.close()
        logger.info("ASR HTTP client closed.")
    logger.info("Main Billing API shutdown complete.")


app = FastAPI(
    title="ML Billing Service API (with ASR)",
    description="API for making ASR predictions with a credit-based billing system.",
    version="0.1.1", # Incremented version
    lifespan=lifespan
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Request validation error: {exc.errors()} for URL: {request.url}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Validation Error"},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled internal server error for request {request.method} {request.url}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred. Please try again later.", "error_type": exc.__class__.__name__},
    )

api_prefix = "/api/v1"
app.include_router(user_controller.router, prefix=api_prefix)
app.include_router(model_controller.router, prefix=api_prefix)
app.include_router(prediction_controller.router, prefix=api_prefix)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the ML Billing Service API (ASR Enabled)!"}

# For uvicorn reload in development (if not using Docker's CMD reload)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
