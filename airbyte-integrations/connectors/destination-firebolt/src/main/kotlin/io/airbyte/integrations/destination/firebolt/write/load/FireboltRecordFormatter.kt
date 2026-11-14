/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.csv.toCsvValue

/** Formats Airbyte record values into CSV values for Firebolt COPY FROM. */
class FireboltRecordFormatter(
    private val columns: List<String>,
) {
    /**
     * Converts a record into a list of CSV values in column order. Columns not present in the
     * record produce an empty string, which Firebolt CSV loading interprets as NULL.
     */
    fun format(record: Map<String, AirbyteValue>): List<Any> =
        columns.map { columnName ->
            if (record.containsKey(columnName)) record[columnName].toCsvValue() else ""
        }
}
