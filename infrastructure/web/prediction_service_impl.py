from core.repositories.prediction_repository import AbstractPredictionService
from core.repositories.ml_model_repository import AbstractMLModelService
from typing import Optional, Any

# from ...core.entities.prediction import Prediction
# from ...core.entities.ml_model import MLModel
import httpx
from config.settings import settings


class HttpServiceBase:
    def __init__(self, url: str, client: httpx.AsyncClient):
        super().__init__()
        self.url = url
        self.client = client


class HttpServicePrediction(AbstractPredictionService, HttpServiceBase):
    async def get_prediction(
        self,
        model_name,
        file: bytes,  # TODO: data class
        lang: Optional[str] = None,
        task: Optional[str] = None,
    ) -> dict[str:Any]:
        form_data = {"model_identifier": model_name}
        if lang:
            form_data["language"] = lang
        if task:
            form_data["task"] = task
        
        files_payload = {
            "audio_file": ("upload.wav", file, "application/octet-stream")
        }

        response = await self.client.post(
            self.url,
            data=form_data,
            files=files_payload,
            timeout=settings.ASR_REQUEST_TIMEOUT_SEC,
        )


        response.raise_for_status()  # Raises for 4xx/5xx client/server errors
        asr_response_data = response.json()

        return asr_response_data


class HttpServiceMLModel(AbstractMLModelService, HttpServiceBase):
    async def upload_model(
        self,
        name: str,
        type: str,
        model_name: str,
    ):
        form_data = {
            "name": name,
            "type": type,
            "model_name": model_name,
        }

        await self.client.post(
            self.url, json=form_data, timeout=settings.ASR_REQUEST_TIMEOUT_SEC
        )
        # TODO: return ok request or model or model id ???
