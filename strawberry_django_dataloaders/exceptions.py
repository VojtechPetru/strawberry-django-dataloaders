from dataclasses import dataclass


class BaseError(Exception):
    message: str
    code: str


@dataclass
class UnsupportedRelationError(BaseError):
    message: str = "Unsupported relation"
    code: str = "unsupported_relation"
