/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType

/**
 * Input for [SelectQuerier] which contains a parameterize SQL query along with its parameter
 * bindings and a description of the columns of the result set.
 */
data class SelectQuery(
    val sql: String,
    val columns: List<Field>,
    val bindings: List<Binding>,
) {
    data class Binding(
        val value: JsonNode,
        val type: LosslessJdbcFieldType<*, *>,
    )
}
