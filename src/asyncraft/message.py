from dataclasses import dataclass
from typing import Any, Tuple


@dataclass(frozen=True)
class Message:

    key: tuple[(int, float, complex, bool, str, tuple, frozenset)] or (int, float, complex, bool, str, tuple, frozenset)
    value: Any
