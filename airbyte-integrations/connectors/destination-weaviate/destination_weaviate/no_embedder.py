#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

from airbyte_cdk.destinations.vector_db_based.embedder import Document, Embedder
from destination_weaviate.config import NoEmbeddingConfigModel


class NoEmbedder(Embedder):
    def __init__(self, config: NoEmbeddingConfigModel):
        super().__init__()

    def check(self) -> Optional[str]:
        return None

    def embed_documents(self, documents: List[Document]) -> List[Optional[List[float]]]:
        return [None for _ in documents]

    @property
    def embedding_dimensions(self) -> int:
        return -1
