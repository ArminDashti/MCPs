from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from chromadb import PersistentClient
from chromadb.api.models import Collection


_client: Optional[PersistentClient] = None


def _get_storage_path() -> Path:
    override = os.environ.get("CHROMA_MCP_STORAGE")
    if override:
        storage_path = Path(override).expanduser()
    else:
        storage_path = Path(__file__).resolve().parents[1] / ".chroma"
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


def get_client() -> PersistentClient:
    global _client
    if _client is None:
        _client = PersistentClient(path=str(_get_storage_path()))
    return _client


def get_collection(name: str) -> Collection:
    if not name:
        raise ValueError("collection name must be provided")
    client = get_client()
    return client.get_or_create_collection(name=name)

