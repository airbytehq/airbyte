/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.schema

import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore

/**
 * Redshift identifier naming rules.
 *
 * We follow the **standard (non-delimited) identifier** rules described at:
 * https://docs.aws.amazon.com/redshift/latest/dg/r_names.html
 *
 * Standard identifier rules:
 * - Begin with an ASCII single-byte alphabetic character or underscore character
 * - Subsequent characters can be ASCII single-byte alphanumeric characters, underscores, etc.
 * - Maximum of 127 bytes in length (truncated with a hash suffix to avoid collisions)
 * - Contain no quotation marks and no spaces.
 * - Not be a reserved system column/SQL key word. // not handled for performance reasons
 * - Identifiers are case-insensitive by default; we follow lowercase globally across Redshift.
 *
 * @return The transformed string suitable for Redshift identifiers.
 */
private const val REDSHIFT_MAX_IDENTIFIER_LENGTH = 127

fun String.toRedshiftCompatibleName(): String {
    // Replace any character that is not a alphanumeric, or an underscore with a single underscore
    var transformed = toAlphanumericAndUnderscore(this)

    // Force lowercase (Redshift convention).
    transformed = transformed.lowercase()

    // Handle Standard identifier Rule (1), If it starts with a digit, prepend an underscore.
    if (transformed.isNotEmpty() && transformed[0].isDigit()) {
        transformed = "_$transformed"
    }

    // Truncate to 127 bytes by keeping a prefix and append a hex hash suffix to avoid collisions.
    if (transformed.length > REDSHIFT_MAX_IDENTIFIER_LENGTH) {
        val hash = transformed.hashCode().toUInt().toString(16).takeLast(8)
        transformed = transformed.take(118) + "_" + hash
    }

    return transformed
}
