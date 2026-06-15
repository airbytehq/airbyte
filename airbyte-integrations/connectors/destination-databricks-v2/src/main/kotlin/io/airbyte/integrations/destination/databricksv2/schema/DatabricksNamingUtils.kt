/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.schema

import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore

/** Maximum identifier length for Databricks (tables, schemas, columns) */
private const val MAX_IDENTIFIER_LENGTH = 255

/** Length reserved for the hash suffix when truncating (underscore + 8-char hash). */
private const val HASH_SUFFIX_LENGTH = 9

fun String.toDatabricksCompatibleName(): String {
    var transformed = toAlphanumericAndUnderscore(this)
    if (transformed.isNotEmpty() && transformed[0].isDigit()) transformed = "_$transformed"

    // Truncate to 255 characters if needed, preserving a hash suffix to avoid collisions.
    if (transformed.length > MAX_IDENTIFIER_LENGTH) {
        val hash = transformed.hashCode().toString().takeLast(8)
        transformed = transformed.take(MAX_IDENTIFIER_LENGTH - HASH_SUFFIX_LENGTH) + "_" + hash
    }

    return transformed
}

/**
 * Sanitizes and lowercases a name for Databricks object identifiers (tables, schemas). Column names
 * should use [toDatabricksCompatibleName] instead, as Databricks preserves column name casing.
 */
fun String.toDatabricksCompatibleNameLowercase(): String = toDatabricksCompatibleName().lowercase()
