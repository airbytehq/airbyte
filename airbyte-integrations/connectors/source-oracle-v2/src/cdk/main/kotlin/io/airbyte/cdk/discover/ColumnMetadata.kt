/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

/** Data class with one field for each [java.sql.ResultSetMetaData] column method. */
data class ColumnMetadata(
    val name: String,
    val label: String,
    val type: SourceType,
    val autoIncrement: Boolean? = null,
    val caseSensitive: Boolean? = null,
    val searchable: Boolean? = null,
    val currency: Boolean? = null,
    val nullable: Boolean? = null,
    val signed: Boolean? = null,
    val displaySize: Int? = null,
    val precision: Int? = null,
    val scale: Int? = null,
)
