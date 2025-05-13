import abc
from typing import Any, Dict 

class AbstractMLModel(abc.ABC):
    """Abstract base class for ML models in the ASR service."""
    @abc.abstractmethod
    async def predict(self, audio_file_path: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Performs inference on the given audio file.
        kwargs can include language, task, etc.
        Should return a dictionary, e.g., {"text": "...", "language": "en", "segments": [...]}
        """
        raise NotImplementedError