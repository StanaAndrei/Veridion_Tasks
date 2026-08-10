from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class DetectionResult:
    technology_name: str
    confidence: float  # 0-1
    proofs: List[str] = field(default_factory=list)