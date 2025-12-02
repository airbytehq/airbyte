/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.util.Jsons
import java.io.OutputStream

/** Estimates the in-memory byte size of a table row based on its [ObjectNode] representation. */
class DefaultRowByteSizeEstimator(
    val estimatedRecordOverheadBytes: Long,
    val estimatedFieldOverheadBytes: Long,
) : JdbcSharedState.RowByteSizeEstimator {
    private var counter: Long = 0L

    override fun apply(record: ObjectNode): Long {
        counter = 0L
        Jsons.writeValue(jsonGenerator, record)
        // The counter value includes the byte count on field name encodings; subtract this.
        // We don't want the estimate to depend on the column name lengths.
        val adjustedFieldOverheadBytes: Long =
            record.fields().asSequence().sumOf { (fieldName: String, _) ->
                val fieldNameOvercount: Int = ",\"".length + fieldName.length + "\":".length
                estimatedFieldOverheadBytes - fieldNameOvercount
            }
        return estimatedRecordOverheadBytes + counter + adjustedFieldOverheadBytes
    }

    private val countingOutputStream =
        object : OutputStream() {
            override fun write(b: Int) {
                counter++
            }
        }

    private val jsonGenerator: JsonGenerator = Jsons.createGenerator(countingOutputStream)
}
