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
     * Genuine nulls (a [NullValue] or a column missing from the record) are emitted as the
     * [NULL_MARKER] sentinel so that the Redshift `COPY` command's `NULL AS` clause loads them as
     * SQL `NULL`. An empty string is emitted as an empty field so it is preserved as an empty
     * string rather than being coerced to `NULL`. This distinction is what keeps empty strings from
     * non-nullable source columns intact.
     */
    fun format(record: Map<String, AirbyteValue>): List<Any> =
        columns.map { columnName ->
            when (val value = record[columnName]) {
                null,
                is NullValue -> NULL_MARKER
                else -> value.toCsvValue()
            }
        }

    companion object {
        /**
         * CSV sentinel used to represent SQL `NULL`. Matches Redshift's default null string and the
         * `NULL AS '\N'` clause in the generated `COPY` command. An empty CSV field is deliberately
         * *not* used, because Redshift cannot distinguish a genuine null from an empty string when
         * both are encoded as empty fields.
         */
        const val NULL_MARKER = "\\N"
    }
}
