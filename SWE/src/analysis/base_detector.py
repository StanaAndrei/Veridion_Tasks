from abc import ABC, abstractmethod
from typing import Optional
from scraper.models import SitePayload
from .models import DetectionResult

class BaseDetector(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The standard name of the technology."""
        pass

    @abstractmethod
    def detect(self, payload: SitePayload) -> Optional[DetectionResult]:
        """Analyzes the payload and returns a DetectionResult if found, else None."""
        pass