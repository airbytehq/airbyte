/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.source.select

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.jdbc.JdbcSelectQuerier
import io.micronaut.context.annotation.DefaultImplementation

@DefaultImplementation(JdbcSelectQuerier::class)
interface SelectQuerier {
    fun executeQuery(
        q: SelectQuery,
        parameters: Parameters = Parameters(),
    ): Result

    data class Parameters(
        val fetchSize: Int? = null,
    )

    interface Result : Iterator<ObjectNode>, AutoCloseable
}
