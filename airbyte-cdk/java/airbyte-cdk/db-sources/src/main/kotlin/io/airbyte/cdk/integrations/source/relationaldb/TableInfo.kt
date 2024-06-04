/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb

/** This class encapsulates all externally relevant Table information. */
data class TableInfo<T>(
    val nameSpace: String,
    val name: String,
    val fields: List<T>,
    val primaryKeys: List<String> = emptyList(),
    val cursorFields: List<String>
)
