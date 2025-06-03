from pydantic import BaseModel
from typing import List


class SearchSchema(BaseModel):
    date_range: List[str] = None
    q: str
    code: str = "all"