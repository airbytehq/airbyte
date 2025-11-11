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

from google.protobuf import timestamp_pb2  # type: ignore
import proto  # type: ignore

__protobuf__ = proto.module(
    package="google.cloud.secrets.v1beta1",
    manifest={
        "Secret",
        "SecretVersion",
        "Replication",
        "SecretPayload",
    },
)


class Secret(proto.Message):
    r"""A [Secret][google.cloud.secrets.v1beta1.Secret] is a logical secret
    whose value and versions can be accessed.

    A [Secret][google.cloud.secrets.v1beta1.Secret] is made up of zero
    or more [SecretVersions][google.cloud.secrets.v1beta1.SecretVersion]
    that represent the secret data.

    Attributes:
        name (str):
            Output only. The resource name of the
            [Secret][google.cloud.secrets.v1beta1.Secret] in the format
            ``projects/*/secrets/*``.
        replication (google.cloud.secretmanager_v1beta1.types.Replication):
            Required. Immutable. The replication policy of the secret
            data attached to the
            [Secret][google.cloud.secrets.v1beta1.Secret].

            The replication policy cannot be changed after the Secret
            has been created.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. The time at which the
            [Secret][google.cloud.secrets.v1beta1.Secret] was created.
        labels (MutableMapping[str, str]):
            The labels assigned to this Secret.

            Label keys must be between 1 and 63 characters long, have a
            UTF-8 encoding of maximum 128 bytes, and must conform to the
            following PCRE regular expression:
            ``[\p{Ll}\p{Lo}][\p{Ll}\p{Lo}\p{N}_-]{0,62}``

            Label values must be between 0 and 63 characters long, have
            a UTF-8 encoding of maximum 128 bytes, and must conform to
            the following PCRE regular expression:
            ``[\p{Ll}\p{Lo}\p{N}_-]{0,63}``

            No more than 64 labels can be assigned to a given resource.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    replication: "Replication" = proto.Field(
        proto.MESSAGE,
        number=2,
        message="Replication",
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=3,
        message=timestamp_pb2.Timestamp,
    )
    labels: MutableMapping[str, str] = proto.MapField(
        proto.STRING,
        proto.STRING,
        number=4,
    )


class SecretVersion(proto.Message):
    r"""A secret version resource in the Secret Manager API.

    Attributes:
        name (str):
            Output only. The resource name of the
            [SecretVersion][google.cloud.secrets.v1beta1.SecretVersion]
            in the format ``projects/*/secrets/*/versions/*``.

            [SecretVersion][google.cloud.secrets.v1beta1.SecretVersion]
            IDs in a [Secret][google.cloud.secrets.v1beta1.Secret] start
            at 1 and are incremented for each subsequent version of the
            secret.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. The time at which the
            [SecretVersion][google.cloud.secrets.v1beta1.SecretVersion]
            was created.
        destroy_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. The time this
            [SecretVersion][google.cloud.secrets.v1beta1.SecretVersion]
            was destroyed. Only present if
            [state][google.cloud.secrets.v1beta1.SecretVersion.state] is
            [DESTROYED][google.cloud.secrets.v1beta1.SecretVersion.State.DESTROYED].
        state (google.cloud.secretmanager_v1beta1.types.SecretVersion.State):
            Output only. The current state of the
            [SecretVersion][google.cloud.secrets.v1beta1.SecretVersion].
    """

    class State(proto.Enum):
        r"""The state of a
        [SecretVersion][google.cloud.secrets.v1beta1.SecretVersion],
        indicating if it can be accessed.

        Values:
            STATE_UNSPECIFIED (0):
                Not specified. This value is unused and
                invalid.
            ENABLED (1):
                The
                [SecretVersion][google.cloud.secrets.v1beta1.SecretVersion]
                may be accessed.
            DISABLED (2):
                The
                [SecretVersion][google.cloud.secrets.v1beta1.SecretVersion]
                may not be accessed, but the secret data is still available
                and can be placed back into the
                [ENABLED][google.cloud.secrets.v1beta1.SecretVersion.State.ENABLED]
                state.
            DESTROYED (3):
                The
                [SecretVersion][google.cloud.secrets.v1beta1.SecretVersion]
                is destroyed and the secret data is no longer stored. A
                version may not leave this state once entered.
        """
        STATE_UNSPECIFIED = 0
        ENABLED = 1
        DISABLED = 2
        DESTROYED = 3

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=2,
        message=timestamp_pb2.Timestamp,
    )
    destroy_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=3,
        message=timestamp_pb2.Timestamp,
    )
    state: State = proto.Field(
        proto.ENUM,
        number=4,
        enum=State,
    )


class Replication(proto.Message):
    r"""A policy that defines the replication configuration of data.

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        automatic (google.cloud.secretmanager_v1beta1.types.Replication.Automatic):
            The [Secret][google.cloud.secrets.v1beta1.Secret] will
            automatically be replicated without any restrictions.

            This field is a member of `oneof`_ ``replication``.
        user_managed (google.cloud.secretmanager_v1beta1.types.Replication.UserManaged):
            The [Secret][google.cloud.secrets.v1beta1.Secret] will only
            be replicated into the locations specified.

            This field is a member of `oneof`_ ``replication``.
    """

    class Automatic(proto.Message):
        r"""A replication policy that replicates the
        [Secret][google.cloud.secrets.v1beta1.Secret] payload without any
        restrictions.

        """

    class UserManaged(proto.Message):
        r"""A replication policy that replicates the
        [Secret][google.cloud.secrets.v1beta1.Secret] payload into the
        locations specified in
        [Replication.UserManaged.replicas][google.cloud.secrets.v1beta1.Replication.UserManaged.replicas]

        Attributes:
            replicas (MutableSequence[google.cloud.secretmanager_v1beta1.types.Replication.UserManaged.Replica]):
                Required. The list of Replicas for this
                [Secret][google.cloud.secrets.v1beta1.Secret].

                Cannot be empty.
        """

        class Replica(proto.Message):
            r"""Represents a Replica for this
            [Secret][google.cloud.secrets.v1beta1.Secret].

            Attributes:
                location (str):
                    The canonical IDs of the location to replicate data. For
                    example: ``"us-east1"``.
            """

            location: str = proto.Field(
                proto.STRING,
                number=1,
            )

        replicas: MutableSequence[
            "Replication.UserManaged.Replica"
        ] = proto.RepeatedField(
            proto.MESSAGE,
            number=1,
            message="Replication.UserManaged.Replica",
        )

    automatic: Automatic = proto.Field(
        proto.MESSAGE,
        number=1,
        oneof="replication",
        message=Automatic,
    )
    user_managed: UserManaged = proto.Field(
        proto.MESSAGE,
        number=2,
        oneof="replication",
        message=UserManaged,
    )


class SecretPayload(proto.Message):
    r"""A secret payload resource in the Secret Manager API. This contains
    the sensitive secret data that is associated with a
    [SecretVersion][google.cloud.secrets.v1beta1.SecretVersion].

    Attributes:
        data (bytes):
            The secret data. Must be no larger than
            64KiB.
    """

    data: bytes = proto.Field(
        proto.BYTES,
        number=1,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
