/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.source.select

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.jdbc.JdbcSelectQuerier
import io.micronaut.context.annotation.DefaultImplementation

@DefaultImplementation(JdbcSelectQuerier::class)
fun interface SelectQuerier {
    fun executeQuery(q: SelectQuery, recordVisitor: RecordVisitor)

    fun interface RecordVisitor {
        /** Returning true interrupts the query. */
        fun visit(record: ObjectNode): Boolean
    }
}
