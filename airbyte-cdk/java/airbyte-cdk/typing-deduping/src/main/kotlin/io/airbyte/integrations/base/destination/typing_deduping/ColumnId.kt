/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

/**
 * In general, callers should not directly instantiate this class. Use [SqlGenerator.buildColumnId]
 * instead.
 *
 * @param name the name of the column in the final table. Callers should prefer [.name] when using
 * the column in a query.
 * @param originalName the name of the field in the raw JSON blob
 * @param canonicalName the name of the field according to the destination. Used for deduping.
 * Useful if a destination warehouse handles columns ignoring case, but preserves case in the table
 * schema.
 */
data class ColumnId(val name: String, val originalName: String, val canonicalName: String) {
    fun name(quote: String): String {
        return quote + name + quote
    }
}
