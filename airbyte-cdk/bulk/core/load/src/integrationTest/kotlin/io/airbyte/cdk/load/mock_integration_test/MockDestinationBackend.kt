/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.test.util.RecordDiffer
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentLinkedQueue

object MockDestinationBackend {
    private val files: ConcurrentHashMap<String, ConcurrentLinkedQueue<OutputRecord>> =
        ConcurrentHashMap()

    fun insert(filename: String, vararg records: OutputRecord) {
        getFile(filename).addAll(records)
    }

    fun upsert(
        filename: String,
        primaryKey: List<List<String>>,
        cursor: List<String>,
        vararg records: OutputRecord
    ) {
        fun getField(path: List<String>, record: OutputRecord): AirbyteValue? {
            var currentValue: ObjectValue = record.data
            // Iterate over the path, except the final element
            for (pathElement in path.subList(0, (path.size - 2).coerceAtLeast(0))) {
                when (val next = currentValue.values[pathElement]) {
                    null,
                    is NullValue -> return null
                    !is ObjectValue -> {
                        throw IllegalStateException(
                            "Attempted to traverse field list in ${record.data} but found non-object value at $pathElement: $next"
                        )
                    }
                    else -> currentValue = next
                }
            }
            return currentValue.values[path.last()]
        }
        fun getPk(record: OutputRecord): List<AirbyteValue?> =
            primaryKey.map { pkField -> getField(pkField, record) }
        fun getCursor(record: OutputRecord): AirbyteValue? = getField(cursor, record)

        val file = getFile(filename)
        records.forEach { incomingRecord ->
            val incomingPk = getPk(incomingRecord)
            // Assume that in dedup mode, we don't have duplicates - so we can just find the first
            // record with the same PK as the incoming record
            val existingRecord =
                file.firstOrNull {
                    RecordDiffer.comparePks(incomingPk, getPk(it), nullEqualsUnset = false) == 0
                }
            if (existingRecord == null) {
                file.add(incomingRecord)
            } else {
                val incomingCursor = getCursor(incomingRecord)
                val existingCursor = getCursor(existingRecord)
                val compare =
                    RecordDiffer.getValueComparator(nullEqualsUnset = false)
                        .compare(incomingCursor, existingCursor)
                // If the incoming record has a later cursor,
                // or the same cursor but a later extractedAt,
                // then upsert. (otherwise discard the incoming record.)
                if (
                    compare > 0 ||
                        (compare == 0 && incomingRecord.extractedAt > existingRecord.extractedAt)
                ) {
                    file.remove(existingRecord)
                    val deletion = getField(listOf("_ab_cdc_deleted_at"), incomingRecord)
                    if (deletion == null || deletion is NullValue) {
                        file.add(incomingRecord)
                    }
                }
            }
        }
    }

    fun commitFrom(srcFilename: String, dstFilename: String) {
        val src = getFile(srcFilename)
        insert(dstFilename, *src.toTypedArray())
        src.clear()
    }

    fun commitAndDedupeFrom(
        srcFilename: String,
        dstFilename: String,
        primaryKey: List<List<String>>,
        cursor: List<String>,
    ) {
        val src = getFile(srcFilename)
        upsert(dstFilename, primaryKey, cursor, *src.toTypedArray())
        src.clear()
    }

    fun readFile(filename: String): List<OutputRecord> {
        return getFile(filename).toList()
    }

    fun deleteOldRecords(filename: String, minGenerationId: Long) {
        getFile(filename).removeAll {
            it.generationId == null || it.generationId!! < minGenerationId
        }
    }

    private fun getFile(filename: String): ConcurrentLinkedQueue<OutputRecord> {
        return files.getOrPut(filename) { ConcurrentLinkedQueue() }
    }
}

object MockDestinationDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        return MockDestinationBackend.readFile(
            MockStreamLoader.getFilename(stream.descriptor.namespace, stream.descriptor.name)
        )
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<String> {
        // Not needed since the test is disabled for file transfer
        throw NotImplementedError()
    }
}
