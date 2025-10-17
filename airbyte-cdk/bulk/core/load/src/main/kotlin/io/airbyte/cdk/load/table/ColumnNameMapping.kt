/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.table

import io.airbyte.cdk.util.invert

/**
 * map from the column name as declared in the schema, to the column name that we'll create in the
 * final (typed) table.
 */
@JvmInline
value class ColumnNameMapping(private val columnNameMapping: Map<String, String>) :
    Map<String, String> by columnNameMapping {
    /**
     * Intended for test use only. If we actually need this at runtime, we probably should only
     * compute the inverse map once.
     */
    // the map is always safe to invert - the entire point of this mapping
    // is that it's 1:1 between original and mapped names.
    // (if any two columns mapped to the same name, then they'd collide in the destination).
    fun originalName(mappedKey: String): String? = columnNameMapping.invert()[mappedKey]
}
