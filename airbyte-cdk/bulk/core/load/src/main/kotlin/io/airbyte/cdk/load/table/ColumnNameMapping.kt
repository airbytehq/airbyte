/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.table

/**
 * map from the column name as declared in the schema, to the column name that we'll create in the
 * final (typed) table.
 */
@JvmInline
value class ColumnNameMapping(private val columnNameMapping: Map<String, String>) :
    Map<String, String> by columnNameMapping
