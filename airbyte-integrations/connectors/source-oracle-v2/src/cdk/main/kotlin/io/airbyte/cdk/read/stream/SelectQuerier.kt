/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.stream

import com.fasterxml.jackson.databind.node.ObjectNode

fun interface SelectQuerier {
    fun executeQuery(q: SelectQuery, recordVisitor: (record: ObjectNode) -> Boolean)
}
