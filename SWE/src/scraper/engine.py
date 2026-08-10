import httpx
import asyncio
from urllib.parse import urljoin
from .models import SitePayload
from ingestion.models import DomainTarget

# Enforce the strict 10-second max timeout across all network operations
TIMEOUT_SETTINGS = httpx.Timeout(10.0)


async def fetch_tier_1(target: DomainTarget) -> SitePayload:
    """
    Tier 1 (Lightweight / Fast): Fires an optimized, non-blocking asynchronous HTTP GET.
    """
    url = target.get_formatted_url()
    robots_url = urljoin(url, "/robots.txt")

    # Follow redirects and ignore SSL errors to maximize successful scrapes
    async with httpx.AsyncClient(timeout=TIMEOUT_SETTINGS, verify=False, follow_redirects=True) as client:
        try:
            # Fetch main page and robots.txt concurrently
            main_req, robots_req = await asyncio.gather(
                client.get(url),
                client.get(robots_url),
                return_exceptions=True
            )

            # Handle potential connection errors on the primary request
            if isinstance(main_req, Exception):
                return SitePayload(url=url, status_code=0, headers={}, cookies={}, html="", error=str(main_req))

            # Safely parse robots.txt if it succeeded, otherwise ignore
            robots_txt = None
            if not isinstance(robots_req, Exception) and robots_req.status_code == 200:
                robots_txt = robots_req.text

            return SitePayload(
                url=str(main_req.url),
                status_code=main_req.status_code,
                headers=dict(main_req.headers),
                cookies=dict(main_req.cookies),
                html=main_req.text,
                robots_txt=robots_txt,
                tier_used=1
            )

        except Exception as e:
            return SitePayload(url=url, status_code=0, headers={}, cookies={}, html="", error=str(e))