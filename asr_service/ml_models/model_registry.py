from typing import Dict, Type, Any
import logging

from ml_models.base import AbstractMLModel
from ml_models.whisper_asr import WhisperASR

from config import asr_settings
from contracts import ASRModelCreate


logger = logging.getLogger(__name__)

class ModelRegistry:
    def __init__(self):
        self._model_type_map: Dict[str, Type[AbstractMLModel]] = {
            "whisper": WhisperASR,
        }
        self._loaded_models: Dict[str, AbstractMLModel] = {}
        logger.info("ASR ModelRegistry initialized.")
        # logger.info(f"Available ASR model types: {list(self._model_type_map.keys())}")
        # logger.info(f"Configured ASR models from settings: {list(asr_settings.MODEL_CONFIGS.keys())}")


    async def add_model(self, model_params: ASRModelCreate) -> AbstractMLModel:
        if model_params.name in self._loaded_models:
            logger.debug(f"ASR model already exist. Use model from cache: {model_params.name}")
            return self._loaded_models[model_params.name]
        
        logger.info(f"Load ASR model: {model_params.name}")
        # TODO: create model_class: AbstractMLModel instead of using config
        model_class = self._model_type_map.get(model_params.type)

        if not model_class:
            logger.error(f"Unknown ASR model type '{model_params.type}' for {model_params.name}.")
            raise ValueError(f"Unknown ASR model type: {model_params.type}")

        try:
            instance_config = {
                "model_name": model_params.model_name,
            }
            if "device" not in instance_config: # ensure device is passed if not in config_params
                instance_config["device"] = asr_settings.DEFAULT_DEVICE

            model_instance = model_class(config=instance_config) 
            self._loaded_models[model_params.name] = model_instance
            logger.info(f"ASR model '{model_params.model_name}' loaded and cached.")

        except Exception as e:
            logger.exception(f"Error loading ASR model '{model_params.name}'")
            raise RuntimeError(f"Failed to load ASR model '{model_params.name}'.") from e


    async def get_model(self, model_identifier: str) -> AbstractMLModel:
        if model_identifier in self._loaded_models:
            logger.debug(f"Using cached ASR model: {model_identifier}")
            return self._loaded_models[model_identifier]
        else:
            # logger.error(f"ASR model identifier '{model_identifier}' not found.")
            # raise ValueError(f"Unknown ASR model identifier: {model_identifier}")

            logger.info(f"Load ASR model: {model_identifier}")
            model_config_from_settings = asr_settings.MODEL_CONFIGS.get(model_identifier)

            if not model_config_from_settings:
                logger.error(f"ASR model identifier '{model_identifier}' not found in config.")
                raise ValueError(f"Unknown ASR model identifier: {model_identifier}")

            model_type = model_config_from_settings.get("type")
            model_class = self._model_type_map.get(model_type)

            if not model_class:
                logger.error(f"Unknown ASR model type '{model_type}' for {model_identifier}.")
                raise ValueError(f"Unknown ASR model type: {model_type}")

            # TODO: use add method
            try:
                instance_config = {
                    "model_name": model_config_from_settings.get("model_name"),
                    **model_config_from_settings.get("config_params", {})
                }
                if "device" not in instance_config:
                    instance_config["device"] = asr_settings.DEFAULT_DEVICE

                model_instance = model_class(config=instance_config)
                self._loaded_models[model_identifier] = model_instance
                logger.info(f"ASR model '{model_identifier}' loaded and cached.")
                return model_instance
            except Exception as e:
                logger.exception(f"Error loading ASR model '{model_identifier}'")
                raise RuntimeError(f"Failed to load ASR model '{model_identifier}'.") from e

model_registry = ModelRegistry()