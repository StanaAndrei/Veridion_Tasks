# src/analysis/detectors/cdn_discovery.py
import re
from urllib.parse import urlparse
from typing import List
from analysis.base_detector import BaseDetector
from analysis.models import DetectionResult
from scraper.models import SitePayload


class CDNDiscoveryDetector(BaseDetector):
    IGNORED_CDNS = {"cdnjs.cloudflare.com", "unpkg.com", "cdn.jsdelivr.net", "code.jquery.com"}

    @property
    def name(self) -> str:
        return "Heuristic: CDNDiscovery"

    def detect(self, payload: SitePayload) -> List[DetectionResult]:
        results = []
        script_srcs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', payload.html, re.I)

        discovered_domains = set()
        for src in script_srcs:
            if src.startswith("http"):
                domain = urlparse(src).netloc
                clean_domain = domain.replace("www.", "")
                if clean_domain not in self.IGNORED_CDNS and clean_domain != urlparse(payload.url).netloc:
                    discovered_domains.add(clean_domain)

        for domain in discovered_domains:
            # Simple heuristic name conversion (e.g., cdn.shopify.com -> shopify)
            parts = domain.split('.')
            tech_guess = parts[-2].capitalize() if len(parts) >= 2 else domain

            results.append(DetectionResult(
                technology_name=f"External Script: {tech_guess}",
                confidence=0.4,
                proofs=[f"Discovered unmapped third-party script origin: {domain}"]
            ))

        return results