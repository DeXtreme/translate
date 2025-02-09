from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Record:
    id: str
    input_text: str
    output_text: str
    created_at: datetime = field(default=datetime.now)
