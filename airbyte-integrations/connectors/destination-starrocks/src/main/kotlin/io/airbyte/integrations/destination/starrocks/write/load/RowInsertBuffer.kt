/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.write.load

import io.airbyte.cdk.load.data.AirbyteValue

/**
 * Accumulates Airbyte records and ships them to a StarRocks table via Stream Load. Two
 * implementations, selected by the connector's `load_format` option:
 * - [CsvRowInsertBuffer] — compact, high-throughput CSV (default).
 * - [JsonRowInsertBuffer] — JSON, which avoids CSV's escaping foot-guns (notably a literal `\N`
 * string being read as NULL) and carries numbers as strings to preserve BIGINT/DECIMAL precision.
 */
interface RowInsertBuffer {
    fun accumulate(recordFields: Map<String, AirbyteValue>)

    suspend fun flush()
}
