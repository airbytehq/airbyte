#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.destinations.vector_db_based.config import (
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    FromFieldEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
)
from airbyte_cdk.destinations.vector_db_based.document_processor import Chunk
from airbyte_cdk.destinations.vector_db_based.embedder import (
    COHERE_VECTOR_SIZE,
    OPEN_AI_VECTOR_SIZE,
    CohereEmbedder,
    FakeEmbedder,
    FromFieldEmbedder,
    OpenAIEmbedder,
)
from airbyte_cdk.models.airbyte_protocol import AirbyteRecordMessage
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


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

    assert embedder.embedding_dimensions == dimensions

    mock_embedding_instance.embed_documents.return_value = [[0] * dimensions] * 2

    chunks = [Chunk(page_content="a", metadata={}, record=AirbyteRecordMessage(stream="mystream", data={}, emitted_at=0)),Chunk(page_content="b", metadata={}, record=AirbyteRecordMessage(stream="mystream", data={}, emitted_at=0))]
    assert embedder.embed_chunks(chunks) == mock_embedding_instance.embed_documents.return_value
    mock_embedding_instance.embed_documents.assert_called_with(["a", "b"])


@pytest.mark.parametrize(
    "field_name, dimensions, metadata, expected_embedding, expected_error",
    (
        ("a", 2, {"a": [1,2]}, [1,2], False),
        ("a", 2, {"b": "b"}, None, True),
        ("a", 2, {}, None, True),
        ("a", 2, {"a": []}, None, True),
        ("a", 2, {"a": [1,2,3]}, None, True),
        ("a", 2, {"a": [1,"2",3]}, None, True),
    )
)
def test_from_field_embedder(field_name, dimensions, metadata, expected_embedding, expected_error):
    embedder = FromFieldEmbedder(FromFieldEmbeddingConfigModel(mode="from_field", dimensions=dimensions, field_name=field_name))
    chunks = [Chunk(page_content="a", metadata=metadata, record=AirbyteRecordMessage(stream="mystream", data=metadata, emitted_at=0))]
    if expected_error:
        with pytest.raises(AirbyteTracedException):
            embedder.embed_chunks(chunks)
    else:
        assert embedder.embed_chunks(chunks) == [expected_embedding]
