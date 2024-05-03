/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.stream

fun interface SelectQueryGenerator {

    fun generateSql(ast: SelectQueryRootNode): SelectQuery
}
