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
    private val varcharColumns: Set<String>,
) {
    /**
     * Converts a record into a list of CSV values in column order.
     *
     * For VARCHAR columns, nulls and missing values are encoded as
     * [RedshiftSqlGenerator.NULL_SENTINEL]. The COPY command's `NULL AS` option maps the sentinel
     * back to SQL NULL, while empty strings are preserved as empty CSV fields (loaded as `''` with
     * [QuoteStrategies.EMPTY]).
     *
     * For all other column types (BIGINT, SUPER, etc.), nulls and missing values produce Java
     * `null`, which FastCSV writes as an unquoted empty field. Redshift auto-nullifies these.
     */
    fun format(record: Map<String, AirbyteValue>): List<String?> =
        columns.map { columnName -> record[columnName].toCsv(columnName in varcharColumns) }

    private fun AirbyteValue?.toCsv(isVarchar: Boolean): String? =
        when {
            this == null || this is NullValue ->
                if (isVarchar) RedshiftSqlGenerator.NULL_SENTINEL else null
            else -> this.toCsvValue().toString()
        }
}
