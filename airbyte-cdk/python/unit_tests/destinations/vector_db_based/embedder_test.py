#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, call

import pytest
from airbyte_cdk.destinations.vector_db_based.config import (
    AzureOpenAIEmbeddingConfigModel,
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    FromFieldEmbeddingConfigModel,
    OpenAICompatibleEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
)
from airbyte_cdk.destinations.vector_db_based.embedder import (
    COHERE_VECTOR_SIZE,
    OPEN_AI_VECTOR_SIZE,
    AzureOpenAIEmbedder,
    CohereEmbedder,
    Document,
    FakeEmbedder,
    FromFieldEmbedder,
    OpenAICompatibleEmbedder,
    OpenAIEmbedder,
)
from airbyte_cdk.models import AirbyteRecordMessage
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


@pytest.mark.parametrize(
    "embedder_class, args, dimensions",
    (
        (OpenAIEmbedder, [OpenAIEmbeddingConfigModel(**{"mode": "openai", "openai_key": "abc"}), 1000], OPEN_AI_VECTOR_SIZE),
        (CohereEmbedder, [CohereEmbeddingConfigModel(**{"mode": "cohere", "cohere_key": "abc"})], COHERE_VECTOR_SIZE),
        (FakeEmbedder, [FakeEmbeddingConfigModel(**{"mode": "fake"})], OPEN_AI_VECTOR_SIZE),
        (
            AzureOpenAIEmbedder,
            [
                AzureOpenAIEmbeddingConfigModel(
                    **{
                        "mode": "azure_openai",
                        "openai_key": "abc",
                        "api_base": "https://my-resource.openai.azure.com",
                        "deployment": "my-deployment",
                    }
                ),
                1000,
            ],
            OPEN_AI_VECTOR_SIZE,
        ),
        (
            OpenAICompatibleEmbedder,
            [
                OpenAICompatibleEmbeddingConfigModel(
                    **{
                        "mode": "openai_compatible",
                        "api_key": "abc",
                        "base_url": "https://my-service.com",
                        "model_name": "text-embedding-ada-002",
                        "dimensions": 50,
                    }
                )
            ],
            50,
        ),
    ),
)
def test_embedder(embedder_class, args, dimensions):
    embedder = embedder_class(*args)
    mock_embedding_instance = MagicMock()
    embedder.embeddings = mock_embedding_instance

    mock_embedding_instance.embed_query.side_effect = Exception("Some error")
    assert embedder.check().startswith("Some error")

    mock_embedding_instance.embed_query.side_effect = None
    assert embedder.check() is None

    assert embedder.embedding_dimensions == dimensions

    mock_embedding_instance.embed_documents.return_value = [[0] * dimensions] * 2

    chunks = [
        Document(page_content="a", record=AirbyteRecordMessage(stream="mystream", data={}, emitted_at=0)),
        Document(page_content="b", record=AirbyteRecordMessage(stream="mystream", data={}, emitted_at=0)),
    ]
    assert embedder.embed_documents(chunks) == mock_embedding_instance.embed_documents.return_value
    mock_embedding_instance.embed_documents.assert_called_with(["a", "b"])


@pytest.mark.parametrize(
    "field_name, dimensions, metadata, expected_embedding, expected_error",
    (
        ("a", 2, {"a": [1, 2]}, [1, 2], False),
        ("a", 2, {"b": "b"}, None, True),
        ("a", 2, {}, None, True),
        ("a", 2, {"a": []}, None, True),
        ("a", 2, {"a": [1, 2, 3]}, None, True),
        ("a", 2, {"a": [1, "2", 3]}, None, True),
    ),
)
def test_from_field_embedder(field_name, dimensions, metadata, expected_embedding, expected_error):
    embedder = FromFieldEmbedder(FromFieldEmbeddingConfigModel(mode="from_field", dimensions=dimensions, field_name=field_name))
    chunks = [Document(page_content="a", record=AirbyteRecordMessage(stream="mystream", data=metadata, emitted_at=0))]
    if expected_error:
        with pytest.raises(AirbyteTracedException):
            embedder.embed_documents(chunks)
    else:
        assert embedder.embed_documents(chunks) == [expected_embedding]


def test_openai_chunking():
    config = OpenAIEmbeddingConfigModel(**{"mode": "openai", "openai_key": "abc"})
    embedder = OpenAIEmbedder(config, 150)
    mock_embedding_instance = MagicMock()
    embedder.embeddings = mock_embedding_instance

    mock_embedding_instance.embed_documents.side_effect = lambda texts: [[0] * OPEN_AI_VECTOR_SIZE] * len(texts)

    chunks = [Document(page_content="a", record=AirbyteRecordMessage(stream="mystream", data={}, emitted_at=0)) for _ in range(1005)]
    assert embedder.embed_documents(chunks) == [[0] * OPEN_AI_VECTOR_SIZE] * 1005
    mock_embedding_instance.embed_documents.assert_has_calls([call(["a"] * 1000), call(["a"] * 5)])
