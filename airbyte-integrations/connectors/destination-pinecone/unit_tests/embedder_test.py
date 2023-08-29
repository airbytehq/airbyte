import unittest
import pytest
from unittest.mock import patch, MagicMock
from typing import Optional
from destination_pinecone.embedder import OpenAIEmbedder, CohereEmbedder, FakeEmbedder, OPEN_AI_VECTOR_SIZE, COHERE_VECTOR_SIZE
from destination_pinecone.config import OpenAIEmbeddingConfigModel, CohereEmbeddingConfigModel, FakeEmbeddingConfigModel

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
