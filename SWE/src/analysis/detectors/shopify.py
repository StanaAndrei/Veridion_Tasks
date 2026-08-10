from typing import Optional
from analysis.base_detector import BaseDetector
from analysis.models import DetectionResult
from scraper.models import SitePayload


class ShopifyDetector(BaseDetector):
    @property
    def name(self) -> str:
        return "Shopify"

    def detect(self, payload: SitePayload) -> Optional[DetectionResult]:
        proofs = []
        confidence = 0.0

        # 1. Header checks
        headers_lower = {k.lower(): v.lower() for k, v in payload.headers.items()}
        if 'x-shopify-stage' in headers_lower or 'x-shopid' in headers_lower:
            proofs.append("Found explicit Shopify routing headers")
            confidence += 0.8

        # 2. Cookie checks
        if any('shopify' in cookie.lower() for cookie in payload.cookies):
            proofs.append("Found Shopify-specific cookies")
            confidence += 0.5

        # 3. HTML signatures
        if 'cdn.shopify.com' in payload.html:
            proofs.append("Detected Shopify CDN links in DOM")
            confidence += 0.6

        if 'Shopify.theme' in payload.html:
            proofs.append("Detected Shopify global JS object")
            confidence += 0.8

        if confidence > 0:
            return DetectionResult(
                technology_name=self.name,
                # Cap confidence at 1.0
                confidence=min(confidence, 1.0),
                proofs=proofs
            )

        return None