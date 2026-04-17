/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.schema

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.integrations.destination.snowflake.sql.escapeJsonIdentifier

/**
 * Transforms a string to be compatible with Snowflake table and column names.
 *
 * @return The transformed string suitable for Snowflake identifiers.
 */
fun String.toSnowflakeCompatibleName(): String {
    var identifier = this

    // Handle empty strings
    if (identifier.isEmpty()) {
        throw ConfigErrorException("Empty string is invalid identifier")
    }

    // Snowflake scripting language does something weird when the `${` bigram shows up in the
    // script so replace these with something else.
    // For completeness, if we trigger this, also replace closing curly braces with underscores.
    if (identifier.contains("\${")) {
        identifier = identifier.replace("$", "_").replace("{", "_").replace("}", "_")
    }

    // Escape double quotes and uppercase
    identifier = escapeJsonIdentifier(identifier).uppercase()

    if (identifier in ANSI_RESERVED_COLUMN_NAMES) {
        identifier = "_$identifier"
    }

    return identifier
}

// Unlike other Snowflake reserved keywords, these cannot be used as column definition names
// even when double-quoted. Prefix with underscore (e.g. LOCALTIME -> _LOCALTIME).
// See https://docs.snowflake.com/en/sql-reference/reserved-keywords
private val ANSI_RESERVED_COLUMN_NAMES =
    setOf(
        "CURRENT_DATE",
        "CURRENT_TIME",
        "CURRENT_TIMESTAMP",
        "CURRENT_USER",
        "LOCALTIME",
        "LOCALTIMESTAMP",
    )
