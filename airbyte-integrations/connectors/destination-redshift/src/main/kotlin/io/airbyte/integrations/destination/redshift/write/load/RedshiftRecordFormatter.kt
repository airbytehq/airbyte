/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.csv.toCsvValue

class RedshiftSchemaRecordFormatter(
    private val columns: List<String>,
) {
    /**
     * Converts a record into a list of CSV values in column order. Columns not present in the
     * record produce an empty string, which Redshift interprets as NULL for the corresponding
     * column type.
     */
    fun format(record: Map<String, AirbyteValue>): List<Any> =
        columns.map { columnName ->
            if (record.containsKey(columnName)) record[columnName].toCsvValue() else ""
        }
}
