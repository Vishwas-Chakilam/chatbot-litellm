from pydantic import BaseModel
from typing import Optional

class chatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
