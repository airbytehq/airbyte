/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.stream

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.ReversibleValueType
import io.airbyte.cdk.discover.ValueType

data class SelectQuery(
    val sql: String,
    val columns: List<Column>,
    val bindings: List<Binding>,
) {

    data class Column(val id: String, val type: ValueType<*>)

    data class Binding(val value: JsonNode, val type: ReversibleValueType<*, *>)
}
