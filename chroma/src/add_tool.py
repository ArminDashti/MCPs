from __future__ import annotations

import json
import uuid
from typing import Any, Iterable

from mcp.types import TextContent, Tool

from .chroma_client import get_collection
from .embeddings import EMBEDDING_DIMENSION, generate_embedding, validate_embedding


def _normalize_list(value: Any, *, name: str) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    raise ValueError(f"{name} must be a list")


def get_tool() -> Tool:
    return Tool(
        name="chroma_add",
        description="Add documents and optional metadata to a Chroma collection.",
        inputSchema={
            "type": "object",
            "properties": {
                "collection_name": {
                    "type": "string",
                    "description": "Name of the Chroma collection."
                },
                "documents": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Documents to store."
                },
                "metadatas": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Optional list of metadata objects aligned with the documents."
                },
                "ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional custom identifiers; generated when omitted."
                },
                "embeddings": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "number"}
                    },
                    "description": (
                        "Optional embeddings matching the documents. If omitted, deterministic"
                        " embeddings are generated automatically."
                    )
                }
            },
            "required": ["collection_name", "documents"],
            "additionalProperties": False
        }
    )


def _ensure_lengths(*lists: Iterable[Any]) -> None:
    lengths = {len(list_item) for list_item in lists if list_item}
    if len(lengths) > 1:
        raise ValueError("documents, metadatas, ids, and embeddings must be the same length")


async def execute(arguments: dict[str, Any]) -> list[TextContent]:
    try:
        collection_name = arguments.get("collection_name", "").strip()
        if not collection_name:
            raise ValueError("collection_name is required")

        documents = _normalize_list(arguments.get("documents"), name="documents")
        if not documents:
            raise ValueError("documents must contain at least one value")

        metadatas = _normalize_list(arguments.get("metadatas"), name="metadatas")
        ids = _normalize_list(arguments.get("ids"), name="ids")
        embeddings = _normalize_list(arguments.get("embeddings"), name="embeddings")

        _ensure_lengths(documents, metadatas, ids, embeddings)

        if not ids:
            ids = [str(uuid.uuid4()) for _ in documents]

        if embeddings:
            for embedding in embeddings:
                if not isinstance(embedding, list):
                    raise ValueError("each embedding must be a list of numbers")
                validate_embedding(embedding)
        else:
            embeddings = [generate_embedding(document) for document in documents]

        metadatas = metadatas or None

        collection = get_collection(collection_name)
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
            embeddings=embeddings
        )

        result = {
            "collection_name": collection_name,
            "count": len(ids),
            "ids": ids,
            "embedding_dimension": EMBEDDING_DIMENSION
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as error:  # pylint: disable=broad-except
        return [TextContent(type="text", text=json.dumps({"error": str(error)}, indent=2))]

