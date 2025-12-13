/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.db

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.integrations.destination.snowflake.sql.QUOTE

/**
 * Escapes double-quotes in a JSON identifier by doubling them. This is legacy -- I don't know why
 * this would be necessary but no harm in keeping it, so I am keeping it.
 *
 * @return The escaped identifier.
 */
fun escapeJsonIdentifier(identifier: String): String {
    // Note that we don't need to escape backslashes here!
    // The only special character in an identifier is the double-quote, which needs to be
    // doubled.
    return identifier.replace(QUOTE, "$QUOTE$QUOTE")
}

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

    return identifier.uppercase()
}
