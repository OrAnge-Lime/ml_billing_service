import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

# Routers
from infrastructure.web.controllers import user_controller, model_controller, prediction_controller
from infrastructure.db.database import create_tables # For initial table creation (or use Alembic)
from config.settings import settings # If needed for app config

# Configure logging
logging.basicConfig(level=logging.INFO) # Настраивает базовую конфигурацию логирования. Сообщения уровня INFO и выше (WARNING, ERROR, CRITICAL) будут выводиться.
logger = logging.getLogger(__name__) # Создает экземпляр логгера 

@asynccontextmanager # Декоратор, превращающий асинхронную функцию-генератор в менеджер контекста.
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info(f"Model Directory: {settings.MODEL_DIRECTORY}")
    logger.info("Creating database tables if they don't exist...")

    await create_tables()
    logger.info("Database tables checked/created.")
    yield

    logger.info("Application shutdown...")

app = FastAPI(
    title="ML Billing Service API",
    version="0.1.0",
    lifespan=lifespan
)

# --- Global Exception Handlers ---
@app.exception_handler(RequestValidationError) # Перехватывает ошибки
async def validation_exception_handler(request: Request, exc: RequestValidationError): 
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

# Add more specific or general exception handlers if needed
# @app.exception_handler(Exception)
# async def general_exception_handler(request: Request, exc: Exception):
#     logger.exception("Unhandled exception occurred") # Log the full traceback
#     return JSONResponse(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         content={"detail": "An internal server error occurred."},
#     )


# --- Routers ---
# Include routers with a prefix, e.g., /api/v1
api_prefix = "/api/v1"
app.include_router(user_controller.router, prefix=api_prefix) # подключает эндпоинты, определенные в соответствующем контроллере
app.include_router(model_controller.router, prefix=api_prefix)
app.include_router(prediction_controller.router, prefix=api_prefix)


# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root():
    """A simple root endpoint to check if the service is running."""
    return {"message": "Welcome to the ML Billing Service API!"}

# --- Run with Uvicorn (for development) ---
# This part is typically not included in main.py but used in the run command
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)