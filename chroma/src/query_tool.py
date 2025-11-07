from __future__ import annotations

import json
from typing import Any

from mcp.types import TextContent, Tool

from .chroma_client import get_collection
from .embeddings import EMBEDDING_DIMENSION, generate_embedding, validate_embedding


def get_tool() -> Tool:
    return Tool(
        name="chroma_query",
        description="Query a Chroma collection by text or precomputed embeddings.",
        inputSchema={
            "type": "object",
            "properties": {
                "collection_name": {
                    "type": "string",
                    "description": "Name of the Chroma collection to query."
                },
                "query_texts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "One or more query strings; embeddings are generated automatically."
                },
                "query_embeddings": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "number"}
                    },
                    "description": "Optional precomputed embeddings to use instead of query_texts."
                },
                "n_results": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 3,
                    "description": "Number of nearest neighbors to return."
                },
                "where": {
                    "type": "object",
                    "description": "Optional metadata filter applied before similarity search."
                }
            },
            "required": ["collection_name"],
            "additionalProperties": False
        }
    )


async def execute(arguments: dict[str, Any]) -> list[TextContent]:
    try:
        collection_name = arguments.get("collection_name", "").strip()
        if not collection_name:
            raise ValueError("collection_name is required")

        query_texts = arguments.get("query_texts")
        query_embeddings = arguments.get("query_embeddings")

        if not query_texts and not query_embeddings:
            raise ValueError("either query_texts or query_embeddings must be provided")

        if query_embeddings:
            if not isinstance(query_embeddings, list):
                raise ValueError("query_embeddings must be a list of embeddings")
            for embedding in query_embeddings:
                if not isinstance(embedding, list):
                    raise ValueError("each query embedding must be a list of numbers")
                validate_embedding(embedding)
            embeddings = query_embeddings
        else:
            if not isinstance(query_texts, list):
                raise ValueError("query_texts must be a list of strings")
            embeddings = [generate_embedding(text) for text in query_texts]

        n_results = int(arguments.get("n_results", 3))
        if n_results <= 0:
            raise ValueError("n_results must be greater than zero")

        where = arguments.get("where")
        if where is not None and not isinstance(where, dict):
            raise ValueError("where must be an object when provided")

        collection = get_collection(collection_name)

        query_kwargs = {
            "query_embeddings": embeddings,
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances", "embeddings"]
        }
        if where:
            query_kwargs["where"] = where

        results = collection.query(**query_kwargs)

        payload = {
            "collection_name": collection_name,
            "query_count": len(embeddings),
            "embedding_dimension": EMBEDDING_DIMENSION,
            "results": results
        }

        return [TextContent(type="text", text=json.dumps(payload, indent=2))]
    except Exception as error:  # pylint: disable=broad-except
        return [TextContent(type="text", text=json.dumps({"error": str(error)}, indent=2))]

