#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from destination_pinecone.config import CohereEmbeddingConfigModel, FakeEmbeddingConfigModel, OpenAIEmbeddingConfigModel
from destination_pinecone.embedder import COHERE_VECTOR_SIZE, OPEN_AI_VECTOR_SIZE, CohereEmbedder, FakeEmbedder, OpenAIEmbedder


@pytest.mark.parametrize(
    "embedder_class, config_model, config_data, dimensions",
    (
        (OpenAIEmbedder, OpenAIEmbeddingConfigModel, {"mode": "openai", "openai_key": "abc"}, OPEN_AI_VECTOR_SIZE),
        (CohereEmbedder, CohereEmbeddingConfigModel, {"mode": "cohere", "cohere_key": "abc"}, COHERE_VECTOR_SIZE),
        (FakeEmbedder, FakeEmbeddingConfigModel, {"mode": "fake"}, OPEN_AI_VECTOR_SIZE),
    )
)
def test_embedder(embedder_class, config_model, config_data, dimensions):
    config = config_model(**config_data)
    embedder = embedder_class(config)
    mock_embedding_instance = MagicMock()
    embedder.embeddings = mock_embedding_instance

    mock_embedding_instance.embed_query.side_effect = Exception("Some error")
    assert embedder.check().startswith("Some error")

    mock_embedding_instance.embed_query.side_effect = None
    assert embedder.check() is None

    assert embedder.langchain_embeddings == mock_embedding_instance

    assert embedder.embedding_dimensions == dimensions
