/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.schema

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.integrations.destination.snowflake.sql.escapeJsonIdentifier

/**
 * ANSI reserved keywords that Snowflake rejects as column names even when quoted. These must be
 * prefixed with an underscore to be used as column names. See:
 * https://docs.snowflake.com/en/sql-reference/reserved-keywords
 */
private val SNOWFLAKE_RESERVED_COLUMN_NAMES =
    setOf(
        "CURRENT_DATE",
        "CURRENT_TIME",
        "CURRENT_TIMESTAMP",
        "CURRENT_USER",
    )

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

    // Escape double quotes
    identifier = escapeJsonIdentifier(identifier)

    // Convert to uppercase before checking reserved keywords
    identifier = identifier.uppercase()

    // Prefix ANSI reserved keywords with underscore
    // These keywords are rejected by Snowflake even when quoted
    if (identifier in SNOWFLAKE_RESERVED_COLUMN_NAMES) {
        identifier = "_$identifier"
    }

    return identifier
}
