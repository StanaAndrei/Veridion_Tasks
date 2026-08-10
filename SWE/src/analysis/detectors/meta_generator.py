# src/analysis/detectors/meta_generator.py
import re
from typing import List
from analysis.base_detector import BaseDetector
from analysis.models import DetectionResult
from scraper.models import SitePayload


class MetaGeneratorDetector(BaseDetector):
    @property
    def name(self) -> str:
        return "Heuristic: MetaGenerator"

    def detect(self, payload: SitePayload) -> List[DetectionResult]:
        results = []
        # Find all <meta name="generator" content="...">
        matches = re.findall(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)["\']', payload.html, re.I)

        for match in set(matches):
            results.append(DetectionResult(
                technology_name=match.strip(),
                confidence=0.5,  # Medium confidence since it's unverified
                proofs=[f"Discovered via unknown <meta name='generator'>: {match}"]
            ))
        return results