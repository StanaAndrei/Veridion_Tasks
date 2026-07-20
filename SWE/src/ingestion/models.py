from dataclasses import dataclass
from urllib.parse import urlparse

@dataclass(frozen=True)
class DomainTarget:
    root_domain: str

    def get_formatted_url(self) -> str:
        """Ensures the domain has a valid scheme for the HTTP client later."""
        domain = self.root_domain.strip()
        if not domain.startswith(("http://", "https://")):
            return f"https://{domain}"
        return domain