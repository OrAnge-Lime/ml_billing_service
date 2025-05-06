import os
import joblib
from typing import Any
import numpy as np # Often needed for scikit-learn models
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ModelExecutionError(Exception):
    """Custom exception for errors during model loading or prediction."""
    pass

class ModelLoader:
    def __init__(self, model_directory: str = settings.MODEL_DIRECTORY):
        self.model_directory = model_directory
        # Simple cache for loaded models (consider size and eviction strategy for prod)
        self._loaded_models = {}
        if not os.path.isdir(self.model_directory):
            logger.warning(f"Model directory '{self.model_directory}' not found. Creating it.")
            os.makedirs(self.model_directory, exist_ok=True)


    def _get_model_path(self, filename: str) -> str:
        return os.path.join(self.model_directory, filename)

    def _load_model(self, filename: str) -> Any:
        """Loads model from cache or disk."""
        if filename in self._loaded_models:
            logger.debug(f"Using cached model: {filename}")
            return self._loaded_models[filename]

        model_path = self._get_model_path(filename)
        logger.info(f"Loading model from: {model_path}")
        try:
            if not os.path.exists(model_path):
                 raise FileNotFoundError(f"Model file not found: {model_path}") # dk_
            
            # TODO: Load model
            model = joblib.load(model_path)
            self._loaded_models[filename] = model # Cache the loaded model
            logger.info(f"Model loaded and cached: {filename}")
            return model
    
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {filename} at {model_path}")
            raise ModelExecutionError(f"Model file '{filename}' not found.") from e
        except Exception as e:
            logger.exception(f"Failed to load model '{filename}': {e}")
            # Avoid caching a failed load attempt or handle specific exceptions dk_
            if filename in self._loaded_models:
                del self._loaded_models[filename]
            raise ModelExecutionError(f"Error loading model '{filename}'.") from e

    async def predict(self, filename: str, input_data: Any) -> Any:
        """Loads model (if not cached) and performs prediction."""
        # Note: Model loading itself is synchronous I/O, but we keep the interface async
        # In a real high-load scenario, loading might be moved to a thread pool executor
        # if it becomes blocking. joblib/pickle loading is often fast enough though.

        try:
            model = self._load_model(filename)

            # Data Validation / Preprocessing (crucial!)
            # This depends heavily on the model. Example for scikit-learn:
            # Assuming input_data is a dict and model expects a 2D numpy array
            # This needs proper schema validation based on model.input_schema if defined
            if not isinstance(input_data, dict):
                 raise ModelExecutionError("Input data must be a dictionary (JSON object).")

            # Example: Convert dict features to numpy array in expected order
            # This is HIGHLY model-specific. A better approach uses pipelines
            # or dedicated preprocessing steps saved with the model.
            # For demo, let's assume features 'f1', 'f2' are needed.
            try:
                 # feature_values = [input_data['f1'], input_data['f2']]
                 # np_input = np.array([feature_values]) # Reshape for single prediction

                 # More flexible: assume input_data is a flat dict of features
                 # Get feature names from the model if possible (e.g., model.feature_names_in_)
                 # Or rely on a fixed order/schema
                 # **Simplest assumption: input_data IS the direct input needed**
                 # e.g., for a simple model, input_data might be [[1, 2, 3]]
                 np_input = np.array(input_data) # Make sure input_data matches model expectation!

            except KeyError as e:
                 raise ModelExecutionError(f"Missing feature in input data: {e}")
            except Exception as e:
                 raise ModelExecutionError(f"Error processing input data: {e}")


            # Actual prediction (synchronous, CPU-bound)
            # Run synchronous CPU-bound code in a thread pool to avoid blocking asyncio event loop
            # However, for quick predictions, direct call might be acceptable overhead.
            # For longer predictions:
            # loop = asyncio.get_running_loop()
            # prediction_result = await loop.run_in_executor(None, model.predict, np_input)

            # Direct call (simpler for now, assumes predict() is fast):
            if not hasattr(model, 'predict'):
                 raise ModelExecutionError(f"Loaded object for '{filename}' has no 'predict' method.")

            prediction_result = model.predict(np_input)

            # Post-processing (e.g., convert numpy types to standard Python types for JSON)
            if isinstance(prediction_result, np.ndarray):
                prediction_result = prediction_result.tolist() # Common conversion

            logger.info(f"Prediction successful for model: {filename}")
            return prediction_result

        except ModelExecutionError as e:
             logger.warning(f"Model execution error for {filename}: {e}")
             raise # Re-raise the specific error
        except Exception as e:
            logger.exception(f"Unexpected error during prediction for model '{filename}': {e}")
            raise ModelExecutionError(f"Prediction failed unexpectedly for model '{filename}'.") from e

# Global instance or inject it where needed
model_loader = ModelLoader()