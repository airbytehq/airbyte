# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.cloud.secretmanager import gapic_version as package_version

__version__ = package_version.__version__


from google.cloud.secretmanager_v1.services.secret_manager_service.async_client import (
    SecretManagerServiceAsyncClient,
)
from google.cloud.secretmanager_v1.services.secret_manager_service.client import (
    SecretManagerServiceClient,
)
from google.cloud.secretmanager_v1.types.resources import (
    CustomerManagedEncryption,
    CustomerManagedEncryptionStatus,
    Replication,
    ReplicationStatus,
    Rotation,
    Secret,
    SecretPayload,
    SecretVersion,
    Topic,
)
from google.cloud.secretmanager_v1.types.service import (
    AccessSecretVersionRequest,
    AccessSecretVersionResponse,
    AddSecretVersionRequest,
    CreateSecretRequest,
    DeleteSecretRequest,
    DestroySecretVersionRequest,
    DisableSecretVersionRequest,
    EnableSecretVersionRequest,
    GetSecretRequest,
    GetSecretVersionRequest,
    ListSecretsRequest,
    ListSecretsResponse,
    ListSecretVersionsRequest,
    ListSecretVersionsResponse,
    UpdateSecretRequest,
)

__all__ = (
    "SecretManagerServiceClient",
    "SecretManagerServiceAsyncClient",
    "CustomerManagedEncryption",
    "CustomerManagedEncryptionStatus",
    "Replication",
    "ReplicationStatus",
    "Rotation",
    "Secret",
    "SecretPayload",
    "SecretVersion",
    "Topic",
    "AccessSecretVersionRequest",
    "AccessSecretVersionResponse",
    "AddSecretVersionRequest",
    "CreateSecretRequest",
    "DeleteSecretRequest",
    "DestroySecretVersionRequest",
    "DisableSecretVersionRequest",
    "EnableSecretVersionRequest",
    "GetSecretRequest",
    "GetSecretVersionRequest",
    "ListSecretsRequest",
    "ListSecretsResponse",
    "ListSecretVersionsRequest",
    "ListSecretVersionsResponse",
    "UpdateSecretRequest",
)
