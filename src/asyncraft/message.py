from dataclasses import dataclass
from typing import Any, Tuple, Union

KeyType = Union[int, float, complex, bool, str, frozenset, Tuple[Union[int, float, complex, bool, str, frozenset], ...]]


@dataclass(frozen=True)
class Message:
    key: KeyType
    value: Any
