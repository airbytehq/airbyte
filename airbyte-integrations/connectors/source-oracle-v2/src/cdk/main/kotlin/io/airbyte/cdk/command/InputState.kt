/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair

/** Union type of the state passed as input to a READ for a source connector. */
sealed interface InputState

data object EmptyInputState : InputState

data class GlobalInputState(
    val global: GlobalStateValue,
    val globalStreams: Map<AirbyteStreamNameNamespacePair, StreamStateValue>,
    /** Conceivably, some streams may undergo a full refresh alongside independently of the rest. */
    val nonGlobalStreams: Map<AirbyteStreamNameNamespacePair, StreamStateValue>,
) : InputState

data class StreamInputState(
    val streams: Map<AirbyteStreamNameNamespacePair, StreamStateValue>,
) : InputState

/** State value for a STATE message of type STREAM. */
data class StreamStateValue(
    @JsonProperty("primary_key") val primaryKey: Map<String, String> = mapOf(),
    @JsonProperty("cursors") val cursors: Map<String, String> = mapOf(),
)

/** State value for a STATE message of type GLOBAL. */
data class GlobalStateValue(@JsonProperty("cdc") val cdc: JsonNode)
