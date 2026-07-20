from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass(frozen=True)
class SitePayload:
    url: str
    status_code: int
    headers: Dict[str, str]
    cookies: Dict[str, str]
    html: str
    robots_txt: Optional[str] = None
    tier_used: int = 1  # 1 for HTTPX, 2 for Playwright (SPA fallback)
    error: Optional[str] = None