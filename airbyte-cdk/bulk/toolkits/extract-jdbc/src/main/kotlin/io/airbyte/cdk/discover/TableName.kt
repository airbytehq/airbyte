/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.discover

/** Models a row for [java.sql.DatabaseMetaData.getTables]. */
data class TableName(
    val catalog: String? = null,
    val schema: String? = null,
    val name: String,
    val type: String,
)
