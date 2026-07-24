/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.csv.toCsvValue

class RedshiftSchemaRecordFormatter(
    private val columns: List<String>,
) {
    /**
     * Converts a record into a list of CSV values in column order.
     *
     * Genuine nulls (a [NullValue] or a column missing from the record) are emitted as null fields,
     * which the CSV writer leaves unquoted so Redshift's `EMPTYASNULL` option loads them as SQL
     * `NULL`. Empty strings are emitted as empty values, which the writer quotes so Redshift
     * preserves them as empty strings instead of converting them to `NULL`.
     */
    fun format(record: Map<String, AirbyteValue>): List<Any?> =
        columns.map { columnName ->
            when (val value = record[columnName]) {
                null,
                is NullValue -> null
                else -> value.toCsvValue()
            }
        }
}
