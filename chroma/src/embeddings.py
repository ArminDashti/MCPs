from __future__ import annotations

import math
from typing import Sequence


EMBEDDING_DIMENSION = 128


def generate_embedding(text: str, *, dimension: int = EMBEDDING_DIMENSION) -> list[float]:
    if dimension <= 0:
        raise ValueError("dimension must be positive")
    vector = [0.0] * dimension
    normalized_text = text.lower()
    if not normalized_text:
        return vector
    for index, char in enumerate(normalized_text):
        if char.isspace():
            continue
        bucket = (ord(char) + index) % dimension
        vector[bucket] += 1.0
    norm = math.sqrt(sum(component * component for component in vector))
    if norm == 0:
        return vector
    return [component / norm for component in vector]


def validate_embedding(embedding: Sequence[float], *, dimension: int = EMBEDDING_DIMENSION) -> None:
    if len(embedding) != dimension:
        raise ValueError(
            f"embedding dimension mismatch: expected {dimension}, received {len(embedding)}"
        )

