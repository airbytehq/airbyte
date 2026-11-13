#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
from typing import Any, Dict, List, Literal, Union

from pydantic.v1 import BaseModel, Field

from airbyte_cdk.destinations.vector_db_based.config import (
    AzureOpenAIEmbeddingConfigModel,
    CohereEmbeddingConfigModel,
    FakeEmbeddingConfigModel,
    FromFieldEmbeddingConfigModel,
    OpenAICompatibleEmbeddingConfigModel,
    OpenAIEmbeddingConfigModel,
    VectorDBConfigModel,
)
from airbyte_cdk.utils.oneof_option_config import OneOfOptionConfig


class UsernamePasswordAuth(BaseModel):
    mode: Literal["username_password"] = Field("username_password", const=True)
    username: str = Field(..., title="Username", description="Username for the Weaviate cluster", order=1)
    password: str = Field(..., title="Password", description="Password for the Weaviate cluster", airbyte_secret=True, order=2)
    scope: str = Field(
        "",
        title="Scope",
        description="Space-separated OIDC scopes to request. Leave empty to use the default scope of the identity provider.",
        order=3,
    )

    class Config(OneOfOptionConfig):
        title = "Username/Password"
        description = "Authenticate using username and password via OIDC (suitable for self-managed Weaviate clusters)"
        discriminator = "mode"


class ClientCredentialsAuth(BaseModel):
    mode: Literal["client_credentials"] = Field("client_credentials", const=True)
    client_secret: str = Field(
        ..., title="Client Secret", description="OIDC client secret of the application", airbyte_secret=True, order=1
    )
    scope: str = Field(
        "",
        title="Scope",
        description="Space-separated OIDC scopes to request. Required by some identity providers, for example Azure (`<client id>/.default`).",
        order=2,
    )

    class Config(OneOfOptionConfig):
        title = "OIDC Client Credentials"
        description = "Authenticate using the OIDC client credentials flow (suitable for clusters behind an identity provider)"
        discriminator = "mode"


class BearerTokenAuth(BaseModel):
    mode: Literal["bearer_token"] = Field("bearer_token", const=True)
    access_token: str = Field(..., title="Access Token", description="OIDC access token", airbyte_secret=True, order=1)
    refresh_token: str = Field(
        "",
        title="Refresh Token",
        description="OIDC refresh token. Without it, syncs that outlast the access token fail.",
        airbyte_secret=True,
        order=2,
    )
    expires_in: int = Field(60, title="Expires In", description="Lifetime of the access token, in seconds", order=3)

    class Config(OneOfOptionConfig):
        title = "OIDC Bearer Token"
        description = "Authenticate using an existing OIDC access token and, optionally, a refresh token"
        discriminator = "mode"


class NoAuth(BaseModel):
    mode: Literal["no_auth"] = Field("no_auth", const=True)

    class Config(OneOfOptionConfig):
        title = "No Authentication"
        description = "Do not authenticate (suitable for locally running test clusters, do not use for clusters with public IP addresses)"
        discriminator = "mode"


class TokenAuth(BaseModel):
    mode: Literal["token"] = Field("token", const=True)
    token: str = Field(..., title="API Key", description="API key for the Weaviate instance", airbyte_secret=True)

    class Config(OneOfOptionConfig):
        title = "API Key"
        description = "Authenticate using an API key (suitable for Weaviate Cloud)"
        discriminator = "mode"


class Header(BaseModel):
    header_key: str = Field(..., title="Header Key")
    value: str = Field(..., title="Header Value", airbyte_secret=True)


class GrpcChannelOption(BaseModel):
    name: str = Field(..., title="Option Name", examples=["grpc.keepalive_time_ms"])
    value: str = Field(..., title="Option Value", description="Integer values are passed as integers", examples=["10000"])


class WeaviateConnectionConfigModel(BaseModel):
    grpc_host: str = Field(
        "",
        title="gRPC Endpoint",
        description="The gRPC endpoint of the cluster as host or host:port. Leave empty to derive it from the public endpoint: "
        "the cluster's gRPC host on port 443 for Weaviate Cloud, the same host on port 50051 otherwise.",
        examples=["my-weaviate-host:50051", "grpc.my-weaviate-host.com:443"],
        order=1,
    )
    grpc_secure: str = Field(
        "auto",
        title="gRPC TLS",
        description="Whether the gRPC connection uses TLS. `auto` uses TLS when the public endpoint uses https.",
        enum=["auto", "enabled", "disabled"],
        order=2,
    )
    timeout_init: float = Field(2, title="Init Timeout", description="Timeout in seconds for the initial connection checks", ge=0, order=3)
    timeout_query: float = Field(
        30, title="Query Timeout", description="Timeout in seconds for schema, tenant and delete requests", ge=0, order=4
    )
    timeout_insert: float = Field(90, title="Insert Timeout", description="Timeout in seconds for batch inserts", ge=0, order=5)
    skip_init_checks: bool = Field(
        False,
        title="Skip Init Checks",
        description="Skip the server version and readiness checks when connecting, for example when a proxy blocks the meta endpoints",
        order=6,
    )
    trust_env: bool = Field(
        False,
        title="Trust Environment",
        description="Read proxy settings and CA bundles from the environment variables (HTTP_PROXY, HTTPS_PROXY, SSL_CERT_FILE, ...)",
        order=7,
    )
    http_proxy: str = Field("", title="HTTP Proxy", description="Proxy URL for http requests", airbyte_secret=True, order=8)
    https_proxy: str = Field("", title="HTTPS Proxy", description="Proxy URL for https requests", airbyte_secret=True, order=9)
    grpc_proxy: str = Field("", title="gRPC Proxy", description="Proxy URL for gRPC requests", airbyte_secret=True, order=10)
    session_pool_connections: int = Field(
        20, title="Session Pool Connections", description="Number of connection pools to cache for http requests", ge=1, order=11
    )
    session_pool_maxsize: int = Field(
        100, title="Session Pool Max Size", description="Maximum number of connections to keep in the http pool", ge=1, order=12
    )
    session_pool_max_retries: int = Field(
        3, title="Session Pool Max Retries", description="Number of retries for failed http requests", ge=0, order=13
    )
    session_pool_timeout: int = Field(
        5, title="Session Pool Timeout", description="Seconds to wait for a free connection from the http pool", ge=0, order=14
    )
    grpc_channel_options: List[GrpcChannelOption] = Field(
        [],
        title="gRPC Channel Options",
        description="Extra gRPC channel arguments, see https://grpc.github.io/grpc/core/group__grpc__arg__keys.html",
        order=15,
    )

    class Config:
        title = "Connection Options"
        description = "Advanced connection settings. The defaults work for Weaviate Cloud and most self-hosted clusters."


class WeaviateIndexingConfigModel(BaseModel):
    host: str = Field(
        ...,
        title="Public Endpoint",
        order=1,
        description="The REST endpoint of the Weaviate cluster. For Weaviate Cloud, paste the REST Endpoint shown in the console; "
        "https is assumed when no scheme is given.",
        examples=["https://my-cluster.weaviate.cloud", "my-cluster.c0.europe-west3.gcp.weaviate.cloud", "http://my-weaviate-host:8080"],
    )
    auth: Union[TokenAuth, UsernamePasswordAuth, ClientCredentialsAuth, BearerTokenAuth, NoAuth] = Field(
        ..., title="Authentication", description="Authentication method", discriminator="mode", type="object", order=2
    )
    batch_size: int = Field(title="Batch Size", description="The number of records to send to Weaviate in each batch", default=128)
    concurrent_requests: int = Field(
        title="Concurrent Batch Requests", description="Number of batches sent to Weaviate in parallel", default=1, ge=1
    )
    consistency_level: str = Field(
        title="Consistency Level",
        description="Replication consistency level for writes and deletes. `default` uses the server default (QUORUM).",
        default="default",
        enum=["default", "ONE", "QUORUM", "ALL"],
    )
    text_field: str = Field(title="Text Field", description="The field in the object that contains the embedded text", default="text")
    tenant_id: str = Field(title="Tenant ID", description="The tenant ID to use for multi tenancy", airbyte_secret=True, default="")
    default_vectorizer: str = Field(
        title="Default Vectorizer",
        description="The vectorizer to use if new classes need to be created",
        default="none",
        enum=[
            "none",
            "text2vec-cohere",
            "text2vec-huggingface",
            "text2vec-openai",
            "text2vec-palm",
            "text2vec-contextionary",
            "text2vec-transformers",
            "text2vec-gpt4all",
        ],
    )
    additional_headers: List[Header] = Field(
        title="Additional headers",
        description="Additional HTTP headers to send with every request.",
        default=[],
        examples=[{"header_key": "X-OpenAI-Api-Key", "value": "my-openai-api-key"}],
    )
    connection: WeaviateConnectionConfigModel = Field(
        default_factory=lambda: WeaviateConnectionConfigModel.parse_obj({}),
        title="Connection Options",
        description="Advanced connection settings: gRPC endpoint, TLS, timeouts, proxies and connection pool. The defaults work for Weaviate Cloud.",
    )

    class Config:
        title = "Indexing"
        schema_extra = {
            "group": "indexing",
            "description": "Indexing configuration",
        }


class NoEmbeddingConfigModel(BaseModel):
    mode: Literal["no_embedding"] = Field("no_embedding", const=True)

    class Config(OneOfOptionConfig):
        title = "No external embedding"
        description = "Do not calculate and pass embeddings to Weaviate. Suitable for clusters with configured vectorizers to calculate embeddings within Weaviate or for classes that should only support regular text search."
        discriminator = "mode"


class ConfigModel(VectorDBConfigModel):
    indexing: WeaviateIndexingConfigModel
    embedding: Union[
        NoEmbeddingConfigModel,
        AzureOpenAIEmbeddingConfigModel,
        OpenAIEmbeddingConfigModel,
        CohereEmbeddingConfigModel,
        FromFieldEmbeddingConfigModel,
        FakeEmbeddingConfigModel,
        OpenAICompatibleEmbeddingConfigModel,
    ] = Field(..., title="Embedding", description="Embedding configuration", discriminator="mode", group="embedding", type="object")

    @classmethod
    def schema(cls, by_alias: bool = True, ref_template: str = "") -> Dict[str, Any]:
        # The CDK only inlines one level of refs, which leaves the nested connection options as $ref/allOf
        schema: Dict[str, Any] = BaseModel.schema.__func__(cls, by_alias)  # type: ignore[attr-defined]
        definitions = schema.pop("definitions", {})

        def inline(node: Any) -> Any:
            if isinstance(node, list):
                return [inline(item) for item in node]
            if not isinstance(node, dict):
                return node
            if "$ref" in node:
                return inline(copy.deepcopy(definitions[node["$ref"].split("/")[-1]]))
            if len(node.get("allOf", [])) == 1:
                merged = {key: value for key, value in node.items() if key != "allOf"}
                return {**inline(node["allOf"][0]), **inline(merged)}
            return {key: inline(value) for key, value in node.items()}

        schema = inline(schema)
        cls.remove_discriminator(schema)
        return schema
