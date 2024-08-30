/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.debezium.relational.history.HistoryRecord
import java.util.*

/**
 * [DebeziumState] maps to the contents of the Debezium offset and schema history files, either
 * prior to or after a call to [DebeziumProducer.run]. [DebeziumState] is also what gets serialized
 * into an Airbyte STATE message as global CDC state.
 */
data class DebeziumState(val offset: Offset, val schema: Optional<Schema>) {

    /** [Offset] maps to the Debezium offset file contents. */
    data class Offset(val debeziumOffset: Map<JsonNode, JsonNode>)

    /** [Schema] maps to the Debezium schema history file contents. */
    data class Schema(val debeziumSchemaHistory: List<HistoryRecord>)
}
