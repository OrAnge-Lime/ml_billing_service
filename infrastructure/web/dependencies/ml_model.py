import httpx
from typing import AsyncGenerator
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

_asr_http_client_instance: httpx.AsyncClient | None = None

async def get_asr_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    FastAPI dependency for an Async HTTP client to communicate with the ASR service.
    Relies on the client being initialized and managed in the app's lifespan.
    """
    global _asr_http_client_instance
    if _asr_http_client_instance is None:
        # This case should ideally be hit only if running outside the main app's lifespan,
        # e.g., in a script or unit test that doesn't set up the app state.
        logger.warning("ASR HTTP client not initialized via app lifespan. Creating temporary client.")
        # Use the configured base URL for the temporary client as well
        async with httpx.AsyncClient(base_url=settings.ASR_SERVICE_URL, timeout=settings.ASR_REQUEST_TIMEOUT_SEC) as client:
            yield client
    else:
        yield _asr_http_client_instance
