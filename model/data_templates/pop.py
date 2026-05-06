from dataclasses import dataclass, field

@dataclass
class Pop:
    size: int
    wealth: float = 100.0
    job: str = "None"  # Reference the profession (e.g., "Miner")
    #needs: dict = field(default_factory=dict)