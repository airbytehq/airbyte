/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.schema

import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore
import java.util.UUID

/**
 * Transforms a string to be compatible with Doris table and column names.
 *
 * Doris identifiers: letters, digits, underscores. Cannot start with a digit.
 */
fun String.toDorisCompatibleName(): String {
    var transformed = toAlphanumericAndUnderscore(this)

    if (transformed.isEmpty()) {
        return "default_name_${UUID.randomUUID().toString().replace("-", "_")}"
    }

    if (transformed[0].isDigit()) {
        transformed = "_$transformed"
    }

    return transformed
}
