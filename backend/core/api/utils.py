from dataclasses import dataclass
from typing import Dict, List, Union

@dataclass
class CustomException(Exception):
    message: str
    status_code: int = 400

@dataclass(frozen=True)
class Response:
    """Response object"""

    message: str
    status_code: int
    data: Union[Dict, List] = None
