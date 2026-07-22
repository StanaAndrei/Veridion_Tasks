from abc import ABC, abstractmethod
from typing import List
from scraper.models import SitePayload
from .models import DetectionResult

class BaseDetector(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The standard name of the detector (not necessarily the tech)."""
        pass

    @abstractmethod
    def detect(self, payload: SitePayload) -> List[DetectionResult]:
        """Analyzes the payload and returns a list of DetectionResults."""
        pass