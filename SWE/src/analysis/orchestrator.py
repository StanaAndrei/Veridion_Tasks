import importlib
import pkgutil
import inspect
from typing import List, Dict
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
                if issubclass(obj, BaseDetector) and obj is not BaseDetector:
                    self.detectors.append(obj())

        print(f"Loaded {len(self.detectors)} detector modules.")

    def analyze(self, payload: SitePayload) -> List[DetectionResult]:
        """Runs all detectors and deduplicates the results."""
        if payload.error:
            return []

        raw_results = []
        for detector in self.detectors:
            try:
                findings = detector.detect(payload)
                if findings:
                    raw_results.extend(findings)
            except Exception as e:
                print(f"Detector {detector.name} failed: {e}")

        return self._deduplicate(raw_results)

    def _deduplicate(self, results: List[DetectionResult]) -> List[DetectionResult]:
        """
        Deduplicates by technology_name. 
        If duplicates exist, it merges the proofs and keeps the highest confidence.
        """
        unique_techs: Dict[str, DetectionResult] = {}

        for result in results:
            key = result.technology_name.lower()

            if key in unique_techs:
                existing = unique_techs[key]

                merged_proofs = list(set(existing.proofs + result.proofs))
                highest_confidence = max(existing.confidence, result.confidence)

                unique_techs[key] = DetectionResult(
                    technology_name=existing.technology_name,
                    confidence=highest_confidence,
                    proofs=merged_proofs
                )
            else:
                unique_techs[key] = result

        return list(unique_techs.values())