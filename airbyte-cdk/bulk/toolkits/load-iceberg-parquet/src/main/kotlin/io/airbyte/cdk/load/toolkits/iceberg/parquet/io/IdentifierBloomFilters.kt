/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.TableProperties

/**
 * Enables Parquet bloom filters for identifier columns on newly written files.
 *
 * Existing files are not rewritten.
 */
fun enableIdentifierBloomFilters(
    table: Table,
    schema: Schema,
    identifierFieldIds: Set<Int>,
) {
    val update = table.updateProperties()
    var changed = false
    identifierFieldIds.forEach { fieldId ->
        val field = schema.findField(fieldId)
        val property = TableProperties.PARQUET_BLOOM_FILTER_COLUMN_ENABLED_PREFIX + field.name()
        if (table.properties()[property] != "true") {
            update.set(property, "true")
            changed = true
        }
    }
    if (changed) {
        update.commit()
    }
}
