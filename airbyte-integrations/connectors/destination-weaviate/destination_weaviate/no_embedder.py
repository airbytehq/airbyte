#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import List, Optional

from airbyte_cdk.destinations.vector_db_based.document_processor import Chunk
from airbyte_cdk.destinations.vector_db_based.embedder import Embedder
from destination_weaviate.config import NoEmbeddingConfigModel


class NoEmbedder(Embedder):
    def __init__(self, config: NoEmbeddingConfigModel):
        super().__init__()

    def check(self) -> Optional[str]:
        return None

    def embed_chunks(self, chunks: List[Chunk]) -> List[None]:
        return [None for _ in chunks]

    @property
    def embedding_dimensions(self) -> int:
        return -1
