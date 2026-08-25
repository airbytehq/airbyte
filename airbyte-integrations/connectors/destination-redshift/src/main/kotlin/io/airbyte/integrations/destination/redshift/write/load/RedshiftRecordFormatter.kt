/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.csv.toCsvValue
import io.airbyte.integrations.destination.redshift.sql.RedshiftSqlGenerator

class RedshiftSchemaRecordFormatter(
    columnsWithTypes: LinkedHashMap<String, String>,
) {
    private val columns = columnsWithTypes.keys.toList()

    /**
     * Columns whose nulls must be encoded as the [RedshiftSqlGenerator.NULL_SENTINEL] token. Only
     * VARCHAR columns need the sentinel to distinguish empty strings from genuine nulls. SUPER
     * columns must NOT use the sentinel because Redshift validates JSON before applying `NULL AS`,
     * and the sentinel is not valid JSON. All other column types (BIGINT, NUMERIC, DATE, etc.)
     * auto-null on empty CSV fields.
     */
    private val sentinelColumns: Set<String> =
        columnsWithTypes.filter { (_, type) -> type.contains("varchar", ignoreCase = true) }.keys

    /**
     * Converts a record into a list of CSV string values in column order.
     *
     * For VARCHAR columns, genuine nulls ([NullValue] or a column missing from the record) are
     * emitted as the [RedshiftSqlGenerator.NULL_SENTINEL] token. The `COPY` command's `NULL AS`
     * option maps this token back to SQL `NULL`, while empty strings are preserved as empty CSV
     * fields (loaded as `''`).
     *
     * For all other column types, nulls are emitted as empty fields. Redshift automatically treats
     * empty fields in non-VARCHAR columns as NULL.
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
