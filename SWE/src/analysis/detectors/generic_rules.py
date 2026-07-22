import json
import re
import os
from typing import List
from analysis.base_detector import BaseDetector
from analysis.models import DetectionResult
from scraper.models import SitePayload


class GenericRulesDetector(BaseDetector):
    def __init__(self):
        self.rules = {}
        rules_path = os.path.join(os.getcwd(), "config", "rules", "technologies.json")
        if os.path.exists(rules_path):
            with open(rules_path, 'r') as f:
                self.rules = json.load(f)

    @property
    def name(self) -> str:
        return "GenericRulesDetector"

    def detect(self, payload: SitePayload) -> List[DetectionResult]:
        results = []
        headers_lower = {k.lower(): str(v).lower() for k, v in payload.headers.items()}

        meta_match = re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)["\']',
                               payload.html, re.I)
        meta_generator_content = meta_match.group(1).lower() if meta_match else None

        for tech_name, signatures in self.rules.items():
            proofs = []
            confidence = 0.0

            # 1. HTML Substring Checks
            for html_sig in signatures.get("html", []):
                if html_sig in payload.html:
                    proofs.append(f"Matched HTML signature: '{html_sig}'")
                    confidence += 0.5

            # 2. Header Checks (Regex)
            for h_key, h_regex in signatures.get("headers", {}).items():
                target_header = headers_lower.get(h_key.lower())
                if target_header and re.search(h_regex, target_header, re.I):
                    proofs.append(f"Matched Header signature: {h_key}")
                    confidence += 0.8

            # 3. Meta Generator Checks
            meta_sig = signatures.get("meta", {}).get("generator")
            if meta_sig and meta_generator_content:
                if re.search(meta_sig, meta_generator_content, re.I):
                    proofs.append(f"Matched Meta Generator: {meta_generator_content}")
                    confidence += 1.0

            if confidence > 0:
                results.append(DetectionResult(
                    technology_name=tech_name,
                    confidence=min(confidence, 1.0),
                    proofs=proofs
                ))

        return results