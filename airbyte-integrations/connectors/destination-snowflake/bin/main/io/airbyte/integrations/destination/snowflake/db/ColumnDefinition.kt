/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.db

/**
 * Jdbc destination column definition representation
 *
 * @param name
 * @param type
 * @param isPrimaryKey
 */
data class ColumnDefinition(val name: String, val type: String, val isPrimaryKey: Boolean)
