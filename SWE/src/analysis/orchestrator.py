import importlib
import pkgutil
import inspect
from typing import List
from scraper.models import SitePayload
from .base_detector import BaseDetector
from .models import DetectionResult
from . import detectors


class RulesEngine:
    def __init__(self):
        self.detectors: List[BaseDetector] = []
        self._load_detectors()

    def _load_detectors(self):
        """Dynamically auto-loads all plugins."""
        for _, module_name, _ in pkgutil.iter_modules(detectors.__path__):
            module = importlib.import_module(f"analysis.detectors.{module_name}")
            for _, obj in inspect.getmembers(module, inspect.isclass):
                # Ensure it's a subclass of BaseDetector but NOT the base class itself
                if issubclass(obj, BaseDetector) and obj is not BaseDetector:
                    self.detectors.append(obj())

        print(f"Loaded {len(self.detectors)} technology detectors.")

    def analyze(self, payload: SitePayload) -> List[DetectionResult]:
        """Runs all loaded detectors against a single payload."""
        results = []
        if payload.error:
            return results  # Skip failed scrapes

        for detector in self.detectors:
            try:
                result = detector.detect(payload)
                if result:
                    results.append(result)
            except Exception as e:
                # In production, we'd log this gracefully so one bad plugin doesn't crash the pipeline
                print(f"Detector {detector.name} failed: {e}")

        return results