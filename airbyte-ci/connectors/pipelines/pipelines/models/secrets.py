# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import hashlib
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from dagger import Client as DaggerClient
from dagger import Secret as DaggerSecret
from google.cloud import secretmanager_v1  # type: ignore
from google.oauth2 import service_account  # type: ignore


class SecretNotFoundError(Exception):
    pass


class SecretString(str):
    """The use of this string subtype will prevent accidental prints of secret value to the console."""

    @property
    def _masked_value(self) -> str:
        return "<SecretString: hidden>"

    def __repr__(self) -> str:
        return self._masked_value


class SecretStore(ABC):
    @abstractmethod
    def _fetch_secret(self, name: str) -> str:
        raise NotImplementedError("SecretStore subclasses must implement a _fetch_secret method")

    def fetch_secret(self, name: str) -> str:
        return SecretString(self._fetch_secret(name))


class GSMSecretStore(SecretStore):
    def __init__(self, gcp_credentials: Secret) -> None:
        service_account_info = json.loads(gcp_credentials.value)
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        self.gsm_client = secretmanager_v1.SecretManagerServiceClient.from_service_account_info(service_account_info)
        # This assumes the service account can only read a single project: the one it was created on.
        # If we want to read secrets from multiple project we'd have to create a secret mapping (in an env var?)
        # Which would map secret store aliases to project ids.
        self.project_id = credentials.project_id

    def _fetch_secret(self, name: str) -> str:
        request = secretmanager_v1.ListSecretVersionsRequest(
            parent=f"projects/{self.project_id}/secrets/{name}",
        )
        secret_versions = self.gsm_client.list_secret_versions(request=request)
        if not secret_versions:
            raise SecretNotFoundError(f"No secret found in GSM for secret {name}")

        for version in secret_versions:
            # 1 means enabled version
            if version.state == 1:
                request = secretmanager_v1.AccessSecretVersionRequest(
                    name=version.name,
                )
                response = self.gsm_client.access_secret_version(request=request)
                return response.payload.data.decode()

        raise SecretNotFoundError(f"No enabled secret version in GSM found for secret {name}")


class EnvVarSecretStore(SecretStore):
    def _fetch_secret(self, name: str) -> str:
        try:
            return os.environ[name]
        except KeyError:
            raise SecretNotFoundError(f"The environment variable {name} is not set.")


class LocalDirectorySecretStore(SecretStore):
    def __init__(self, local_directory_path: Path) -> None:
        if not local_directory_path.exists() or not local_directory_path.is_dir():
            raise ValueError(f"The path {local_directory_path} does not exists on your filesystem or is not a directory.")
        self.local_directory_path = local_directory_path

    def _fetch_secret(self, name: str) -> str:
        secret_path = self.local_directory_path / name
        if not secret_path.exists():
            raise SecretNotFoundError(f"The file {secret_path} does not exists.")
        if not secret_path.is_file():
            raise SecretNotFoundError(f"The path {secret_path} is not a file.")
        return secret_path.read_text()

    def get_all_secrets(self) -> List[Secret]:
        return [
            Secret(
                name=str(file.relative_to(self.local_directory_path)),
                secret_store=self,
                file_name=str(file.relative_to(self.local_directory_path)),
            )
            for file in self.local_directory_path.rglob("*")
            if file.is_file()
        ]


class InMemorySecretStore(SecretStore):
    def __init__(self) -> None:
        self._store: Dict[str, str] = {}

    def add_secret(self, name: str, value: str) -> Secret:
        self._store[name] = value
        return Secret(name, self)

    def _fetch_secret(self, name: str) -> str:
        try:
            return self._store[name]
        except KeyError:
            raise SecretNotFoundError(f"Secret named {name} can't be found in the in memory secret store")


@dataclass
class Secret:
    name: str
    secret_store: SecretStore
    file_name: str | None = None

    def __post_init__(self) -> None:
        self.value: str = self.secret_store.fetch_secret(self.name)
        self.value_hash: str = self._get_value_hash(self.value)

    @staticmethod
    def _get_value_hash(value: str) -> str:
        byte_string = value.encode("utf-8")
        md5_hash = hashlib.md5()
        md5_hash.update(byte_string)
        return md5_hash.hexdigest()[:20]

    def as_dagger_secret(self, dagger_client: DaggerClient) -> DaggerSecret:
        return dagger_client.set_secret(self.value_hash, self.value)
