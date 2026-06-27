/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.sql

/**
 * SQL escaping utilities for Redshift identifiers and string literals.
 *
 * Redshift follows PostgreSQL quoting conventions:
 * - Identifiers are double-quoted: `"my_table"`
 * - String literals are single-quoted: `'my_value'`
 */
object RedshiftSqlEscapeUtils {
    /**
     * Wraps an identifier in double quotes per Redshift/PostgreSQL convention. Escapes any embedded
     * double-quote characters by doubling them (`"` -> `""`).
     *
     * Example: `my"col` -> `"my""col"`
     */
    fun quoteIdentifier(identifier: String): String = "\"${identifier.replace("\"", "\"\"")}\""

    /**
     * Escapes a string value for use in single-quoted SQL literals. Doubles any embedded
     * single-quote characters (`'` -> `''`).
     *
     * Example: `O'Brien` -> `O''Brien`
     */
    fun escapeSqlString(value: String): String = value.replace("'", "''")
}
