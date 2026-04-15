/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.schema

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
 * - Maximum of 127 bytes in length
 * - Contain no quotation marks and no spaces.
 * - Not be a reserved system column/SQL key word. // not handled for performnace reasons
 *
 * Identifiers are case-insensitive by default; we follow lowercase globally across Redshift.
 *
 * Compatibility note: Below features are intentionally NOT handled, to stay compatible with v1:
 * - Empty string handling -- V1 does not produce a fallback name for empty inputs.
 * - Max length truncation -- V1 does not explicitly truncate identifiers to 127 characters.
 *
 * @return The transformed string suitable for Redshift identifiers.
 */
fun String.toRedshiftCompatibleName(): String {
    // Replace any character that is not a alphanumeric, or an underscore with a single underscore
    var transformed = toAlphanumericAndUnderscore(this)

    // Force lowercase (Redshift convention).
    transformed = transformed.lowercase()

    // Handle Standard identifier Rule (1), If it starts with a digit, prepend an underscore.
    if (transformed.isNotEmpty() && transformed[0].isDigit()) {
        transformed = "_$transformed"
    }

    return transformed
}
