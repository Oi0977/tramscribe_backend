from typing import TypeVar, Generic, Union
from pydantic import BaseModel

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    code: int = 200
    status: str = 'success'
    data: T|None = None