from pydantic import BaseModel
from typing import Optional


class LeaderSchema(BaseModel):
    category: str
    rank: int
    player_name: str
    value: str
    player_url: Optional[str]

    model_config = {
        "from_attributes": True,
    }
