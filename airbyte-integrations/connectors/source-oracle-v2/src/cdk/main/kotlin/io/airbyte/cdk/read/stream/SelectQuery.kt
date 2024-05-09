/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.stream

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.ReversibleFieldType
import io.airbyte.cdk.discover.Field

data class SelectQuery(
    val sql: String,
    val columns: List<Field>,
    val bindings: List<Binding>,
) {

    data class Binding(val value: JsonNode, val type: ReversibleFieldType)
}
