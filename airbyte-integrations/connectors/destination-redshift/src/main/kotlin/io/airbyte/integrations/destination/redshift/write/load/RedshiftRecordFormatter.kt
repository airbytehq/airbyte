/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.csv.toCsvValue

class RedshiftSchemaRecordFormatter(
    private val columns: List<String>,
    private val nullSentinel: String,
) {
    /**
     * Converts a record into a list of CSV values in column order.
     *
     * Genuine nulls (a [NullValue] or a column missing from the record) are emitted as an
     * improbable sentinel token that the `COPY` command's `NULL AS` option maps to SQL `NULL`.
     * Empty strings are emitted as empty fields so Redshift preserves them as empty strings.
     */
    fun format(record: Map<String, AirbyteValue>): List<String> =
        columns.map { columnName ->
            when (val value = record[columnName]) {
                null,
                is NullValue -> nullSentinel
                else -> value.toCsvValue().toString()
            }
        }
}
