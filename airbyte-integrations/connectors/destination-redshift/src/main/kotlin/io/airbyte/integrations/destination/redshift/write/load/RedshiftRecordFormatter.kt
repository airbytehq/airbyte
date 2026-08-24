/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.integrations.destination.redshift.sql.RedshiftSqlGenerator

class RedshiftSchemaRecordFormatter(
    private val columns: List<String>,
    private val sentinelColumns: Set<String>,
) {
    /**
     * Converts a record into a list of CSV string values in column order.
     *
     * For VARCHAR and SUPER columns (those in [sentinelColumns]), genuine nulls ([NullValue] or a
     * column missing from the record) are emitted as the [RedshiftSqlGenerator.NULL_SENTINEL]
     * token. The `COPY` command's `NULL AS` option maps this token back to SQL `NULL`, while empty
     * strings are preserved as empty CSV fields (loaded as `''`).
     *
     * For all other column types (BIGINT, NUMERIC, DATE, etc.), nulls are emitted as empty fields.
     * Redshift automatically treats empty fields in non-VARCHAR columns as NULL.
     */
    fun format(record: Map<String, AirbyteValue>): List<String> =
        columns.map { columnName ->
            val value = record[columnName]
            when {
                (value == null || value is NullValue) && columnName in sentinelColumns ->
                    RedshiftSqlGenerator.NULL_SENTINEL
                value == null || value is NullValue -> ""
                else -> value.toCsvValue().toString()
            }
        }
}
