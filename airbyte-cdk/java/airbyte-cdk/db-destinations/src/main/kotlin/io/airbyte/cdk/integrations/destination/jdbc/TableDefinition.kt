/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc

/**
 * Jdbc destination table definition representation with a map of column names to column definitions
 *
 * @param columns
 */
@JvmRecord data class TableDefinition(val columns: LinkedHashMap<String, ColumnDefinition>)
