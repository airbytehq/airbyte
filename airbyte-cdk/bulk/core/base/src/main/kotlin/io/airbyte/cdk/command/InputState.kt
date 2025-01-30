/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.StreamIdentifier

/** Union type of the state passed as input to a READ for a source connector. */
sealed interface InputState

data object EmptyInputState : InputState

data class GlobalInputState(
    val global: OpaqueStateValue,
    val globalStreams: Map<StreamIdentifier, OpaqueStateValue>,
    /** Conceivably, some streams may undergo a full refresh alongside independently of the rest. */
    val nonGlobalStreams: Map<StreamIdentifier, OpaqueStateValue>,
) : InputState

data class StreamInputState(
    val streams: Map<StreamIdentifier, OpaqueStateValue>,
) : InputState

/** State values are opaque for the CDK, the schema is owned by the connector. */
typealias OpaqueStateValue = JsonNode
