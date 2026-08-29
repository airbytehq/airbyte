/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.sql

/**
 * SQL escaping utilities for Firebolt identifiers and string literals.
 *
 * Firebolt identifiers are double-quoted and are case-sensitive when quoted. Unquoted identifiers
 * are lower-cased.
 */
object FireboltSqlEscapeUtils {
    /** Wraps an identifier in double quotes and escapes embedded double quotes by doubling them. */
    fun quoteIdentifier(identifier: String): String = "\"${identifier.replace("\"", "\"\"")}\""

    /** Escapes a string value for use in single-quoted SQL literals. */
    fun escapeSqlString(value: String): String = value.replace("'", "''")
}
