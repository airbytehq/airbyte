/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.schema

import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore
import java.util.UUID

/**
 * Transforms a string to be compatible with ClickHouse table and column names.
 *
 * @return The transformed string suitable for ClickHouse identifiers.
 */
fun String.toClickHouseCompatibleName(): String {
    // 1. Replace any character that is not a letter,
    //    a digit (0-9), or an underscore (_) with a single underscore.
    var transformed = toAlphanumericAndUnderscore(this)

    // 2.Do not allow empty strings.
    if (transformed.isEmpty()) {
        return "default_name_${UUID.randomUUID()}" // A fallback name if the input results in an
        // empty string
    }

    // 3. Ensure the identifier does not start with a digit.
    //    If it starts with a digit, prepend an underscore.
    if (transformed[0].isDigit()) {
        transformed = "_$transformed"
    }

    return transformed
}
