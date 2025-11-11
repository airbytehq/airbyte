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
from __future__ import annotations

from typing import MutableMapping, MutableSequence

from google.protobuf import field_mask_pb2  # type: ignore
import proto  # type: ignore

from google.cloud.secretmanager_v1beta2.types import resources

__protobuf__ = proto.module(
    package="google.cloud.secretmanager.v1beta2",
    manifest={
        "ListSecretsRequest",
        "ListSecretsResponse",
        "CreateSecretRequest",
        "AddSecretVersionRequest",
        "GetSecretRequest",
        "ListSecretVersionsRequest",
        "ListSecretVersionsResponse",
        "GetSecretVersionRequest",
        "UpdateSecretRequest",
        "AccessSecretVersionRequest",
        "AccessSecretVersionResponse",
        "DeleteSecretRequest",
        "DisableSecretVersionRequest",
        "EnableSecretVersionRequest",
        "DestroySecretVersionRequest",
    },
)


class ListSecretsRequest(proto.Message):
    r"""Request message for
    [SecretManagerService.ListSecrets][google.cloud.secretmanager.v1beta2.SecretManagerService.ListSecrets].

    Attributes:
        parent (str):
            Required. The resource name of the project associated with
            the [Secrets][google.cloud.secretmanager.v1beta2.Secret], in
            the format ``projects/*`` or ``projects/*/locations/*``
        page_size (int):
            Optional. The maximum number of results to be
            returned in a single page. If set to 0, the
            server decides the number of results to return.
            If the number is greater than 25000, it is
            capped at 25000.
        page_token (str):
            Optional. Pagination token, returned earlier via
            [ListSecretsResponse.next_page_token][google.cloud.secretmanager.v1beta2.ListSecretsResponse.next_page_token].
        filter (str):
            Optional. Filter string, adhering to the rules in
            `List-operation
            filtering <https://cloud.google.com/secret-manager/docs/filtering>`__.
            List only secrets matching the filter. If filter is empty,
            all secrets are listed.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=2,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=3,
    )
    filter: str = proto.Field(
        proto.STRING,
        number=4,
    )


class ListSecretsResponse(proto.Message):
    r"""Response message for
    [SecretManagerService.ListSecrets][google.cloud.secretmanager.v1beta2.SecretManagerService.ListSecrets].

    Attributes:
        secrets (MutableSequence[google.cloud.secretmanager_v1beta2.types.Secret]):
            The list of
            [Secrets][google.cloud.secretmanager.v1beta2.Secret] sorted
            in reverse by create_time (newest first).
        next_page_token (str):
            A token to retrieve the next page of results. Pass this
            value in
            [ListSecretsRequest.page_token][google.cloud.secretmanager.v1beta2.ListSecretsRequest.page_token]
            to retrieve the next page.
        total_size (int):
            The total number of
            [Secrets][google.cloud.secretmanager.v1beta2.Secret] but 0
            when the
            [ListSecretsRequest.filter][google.cloud.secretmanager.v1beta2.ListSecretsRequest.filter]
            field is set.
    """

    @property
    def raw_page(self):
        return self

    secrets: MutableSequence[resources.Secret] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=resources.Secret,
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )
    total_size: int = proto.Field(
        proto.INT32,
        number=3,
    )


class CreateSecretRequest(proto.Message):
    r"""Request message for
    [SecretManagerService.CreateSecret][google.cloud.secretmanager.v1beta2.SecretManagerService.CreateSecret].

    Attributes:
        parent (str):
            Required. The resource name of the project to associate with
            the [Secret][google.cloud.secretmanager.v1beta2.Secret], in
            the format ``projects/*`` or ``projects/*/locations/*``.
        secret_id (str):
            Required. This must be unique within the project.

            A secret ID is a string with a maximum length of 255
            characters and can contain uppercase and lowercase letters,
            numerals, and the hyphen (``-``) and underscore (``_``)
            characters.
        secret (google.cloud.secretmanager_v1beta2.types.Secret):
            Required. A
            [Secret][google.cloud.secretmanager.v1beta2.Secret] with
            initial field values.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    secret_id: str = proto.Field(
        proto.STRING,
        number=2,
    )
    secret: resources.Secret = proto.Field(
        proto.MESSAGE,
        number=3,
        message=resources.Secret,
    )


class AddSecretVersionRequest(proto.Message):
    r"""Request message for
    [SecretManagerService.AddSecretVersion][google.cloud.secretmanager.v1beta2.SecretManagerService.AddSecretVersion].

    Attributes:
        parent (str):
            Required. The resource name of the
            [Secret][google.cloud.secretmanager.v1beta2.Secret] to
            associate with the
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion]
            in the format ``projects/*/secrets/*`` or
            ``projects/*/locations/*/secrets/*``.
        payload (google.cloud.secretmanager_v1beta2.types.SecretPayload):
            Required. The secret payload of the
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion].
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    payload: resources.SecretPayload = proto.Field(
        proto.MESSAGE,
        number=2,
        message=resources.SecretPayload,
    )


class GetSecretRequest(proto.Message):
    r"""Request message for
    [SecretManagerService.GetSecret][google.cloud.secretmanager.v1beta2.SecretManagerService.GetSecret].

    Attributes:
        name (str):
            Required. The resource name of the
            [Secret][google.cloud.secretmanager.v1beta2.Secret], in the
            format ``projects/*/secrets/*`` or
            ``projects/*/locations/*/secrets/*``.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ListSecretVersionsRequest(proto.Message):
    r"""Request message for
    [SecretManagerService.ListSecretVersions][google.cloud.secretmanager.v1beta2.SecretManagerService.ListSecretVersions].

    Attributes:
        parent (str):
            Required. The resource name of the
            [Secret][google.cloud.secretmanager.v1beta2.Secret]
            associated with the
            [SecretVersions][google.cloud.secretmanager.v1beta2.SecretVersion]
            to list, in the format ``projects/*/secrets/*`` or
            ``projects/*/locations/*/secrets/*``.
        page_size (int):
            Optional. The maximum number of results to be
            returned in a single page. If set to 0, the
            server decides the number of results to return.
            If the number is greater than 25000, it is
            capped at 25000.
        page_token (str):
            Optional. Pagination token, returned earlier via
            ListSecretVersionsResponse.next_page_token][].
        filter (str):
            Optional. Filter string, adhering to the rules in
            `List-operation
            filtering <https://cloud.google.com/secret-manager/docs/filtering>`__.
            List only secret versions matching the filter. If filter is
            empty, all secret versions are listed.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=2,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=3,
    )
    filter: str = proto.Field(
        proto.STRING,
        number=4,
    )


class ListSecretVersionsResponse(proto.Message):
    r"""Response message for
    [SecretManagerService.ListSecretVersions][google.cloud.secretmanager.v1beta2.SecretManagerService.ListSecretVersions].

    Attributes:
        versions (MutableSequence[google.cloud.secretmanager_v1beta2.types.SecretVersion]):
            The list of
            [SecretVersions][google.cloud.secretmanager.v1beta2.SecretVersion]
            sorted in reverse by create_time (newest first).
        next_page_token (str):
            A token to retrieve the next page of results. Pass this
            value in
            [ListSecretVersionsRequest.page_token][google.cloud.secretmanager.v1beta2.ListSecretVersionsRequest.page_token]
            to retrieve the next page.
        total_size (int):
            The total number of
            [SecretVersions][google.cloud.secretmanager.v1beta2.SecretVersion]
            but 0 when the
            [ListSecretsRequest.filter][google.cloud.secretmanager.v1beta2.ListSecretsRequest.filter]
            field is set.
    """

    @property
    def raw_page(self):
        return self

    versions: MutableSequence[resources.SecretVersion] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=resources.SecretVersion,
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )
    total_size: int = proto.Field(
        proto.INT32,
        number=3,
    )


class GetSecretVersionRequest(proto.Message):
    r"""Request message for
    [SecretManagerService.GetSecretVersion][google.cloud.secretmanager.v1beta2.SecretManagerService.GetSecretVersion].

    Attributes:
        name (str):
            Required. The resource name of the
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion]
            in the format ``projects/*/secrets/*/versions/*`` or
            ``projects/*/locations/*/secrets/*/versions/*``.

            ``projects/*/secrets/*/versions/latest`` or
            ``projects/*/locations/*/secrets/*/versions/latest`` is an
            alias to the most recently created
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion].
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class UpdateSecretRequest(proto.Message):
    r"""Request message for
    [SecretManagerService.UpdateSecret][google.cloud.secretmanager.v1beta2.SecretManagerService.UpdateSecret].

    Attributes:
        secret (google.cloud.secretmanager_v1beta2.types.Secret):
            Required.
            [Secret][google.cloud.secretmanager.v1beta2.Secret] with
            updated field values.
        update_mask (google.protobuf.field_mask_pb2.FieldMask):
            Required. Specifies the fields to be updated.
    """

    secret: resources.Secret = proto.Field(
        proto.MESSAGE,
        number=1,
        message=resources.Secret,
    )
    update_mask: field_mask_pb2.FieldMask = proto.Field(
        proto.MESSAGE,
        number=2,
        message=field_mask_pb2.FieldMask,
    )


class AccessSecretVersionRequest(proto.Message):
    r"""Request message for
    [SecretManagerService.AccessSecretVersion][google.cloud.secretmanager.v1beta2.SecretManagerService.AccessSecretVersion].

    Attributes:
        name (str):
            Required. The resource name of the
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion]
            in the format ``projects/*/secrets/*/versions/*`` or
            ``projects/*/locations/*/secrets/*/versions/*``.

            ``projects/*/secrets/*/versions/latest`` or
            ``projects/*/locations/*/secrets/*/versions/latest`` is an
            alias to the most recently created
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion].
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class AccessSecretVersionResponse(proto.Message):
    r"""Response message for
    [SecretManagerService.AccessSecretVersion][google.cloud.secretmanager.v1beta2.SecretManagerService.AccessSecretVersion].

    Attributes:
        name (str):
            The resource name of the
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion]
            in the format ``projects/*/secrets/*/versions/*`` or
            ``projects/*/locations/*/secrets/*/versions/*``.
        payload (google.cloud.secretmanager_v1beta2.types.SecretPayload):
            Secret payload
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    payload: resources.SecretPayload = proto.Field(
        proto.MESSAGE,
        number=2,
        message=resources.SecretPayload,
    )


class DeleteSecretRequest(proto.Message):
    r"""Request message for
    [SecretManagerService.DeleteSecret][google.cloud.secretmanager.v1beta2.SecretManagerService.DeleteSecret].

    Attributes:
        name (str):
            Required. The resource name of the
            [Secret][google.cloud.secretmanager.v1beta2.Secret] to
            delete in the format ``projects/*/secrets/*``.
        etag (str):
            Optional. Etag of the
            [Secret][google.cloud.secretmanager.v1beta2.Secret]. The
            request succeeds if it matches the etag of the currently
            stored secret object. If the etag is omitted, the request
            succeeds.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    etag: str = proto.Field(
        proto.STRING,
        number=2,
    )


class DisableSecretVersionRequest(proto.Message):
    r"""Request message for
    [SecretManagerService.DisableSecretVersion][google.cloud.secretmanager.v1beta2.SecretManagerService.DisableSecretVersion].

    Attributes:
        name (str):
            Required. The resource name of the
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion]
            to disable in the format ``projects/*/secrets/*/versions/*``
            or ``projects/*/locations/*/secrets/*/versions/*``.
        etag (str):
            Optional. Etag of the
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion].
            The request succeeds if it matches the etag of the currently
            stored secret version object. If the etag is omitted, the
            request succeeds.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    etag: str = proto.Field(
        proto.STRING,
        number=2,
    )


class EnableSecretVersionRequest(proto.Message):
    r"""Request message for
    [SecretManagerService.EnableSecretVersion][google.cloud.secretmanager.v1beta2.SecretManagerService.EnableSecretVersion].

    Attributes:
        name (str):
            Required. The resource name of the
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion]
            to enable in the format ``projects/*/secrets/*/versions/*``
            or ``projects/*/locations/*/secrets/*/versions/*``.
        etag (str):
            Optional. Etag of the
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion].
            The request succeeds if it matches the etag of the currently
            stored secret version object. If the etag is omitted, the
            request succeeds.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    etag: str = proto.Field(
        proto.STRING,
        number=2,
    )


class DestroySecretVersionRequest(proto.Message):
    r"""Request message for
    [SecretManagerService.DestroySecretVersion][google.cloud.secretmanager.v1beta2.SecretManagerService.DestroySecretVersion].

    Attributes:
        name (str):
            Required. The resource name of the
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion]
            to destroy in the format ``projects/*/secrets/*/versions/*``
            or ``projects/*/locations/*/secrets/*/versions/*``.
        etag (str):
            Optional. Etag of the
            [SecretVersion][google.cloud.secretmanager.v1beta2.SecretVersion].
            The request succeeds if it matches the etag of the currently
            stored secret version object. If the etag is omitted, the
            request succeeds.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    etag: str = proto.Field(
        proto.STRING,
        number=2,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
