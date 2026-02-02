/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

const val STAGE_NAME_PREFIX = "airbyte_stage_"
internal const val QUOTE: String = "\""

fun sqlEscape(part: String) = part.replace("\\", "\\\\").replace("'", "\\'").replace("\"", "\\\"")

/**
 * Surrounds the string instance with double quotation marks (e.g. "some string" -> "\"some
 * string\"").
 */
fun String.quote() = "$QUOTE$this$QUOTE"

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
