/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components.debezium

import io.airbyte.cdk.components.ConsumerComponent
import io.airbyte.commons.json.Jsons
import java.util.*
import java.util.concurrent.atomic.AtomicLong
import kotlin.collections.ArrayList

/**
 * [ConsumerComponent] for Debezium. Internally, as well as in the [Sequence] returned by [flush],
 * the records are stored as byte arrays containing the JSON serialization of the debezium change
 * data event value.
 * - [maxRecords] is how many records to accept before reporting the need to checkpoint.
 * - [maxRecordBytes] is the same but for record bytes.
 */
class DebeziumConsumer
private constructor(
    @JvmField val maxRecords: Long,
    @JvmField val maxRecordBytes: Long,
) : ConsumerComponent<DebeziumRecord> {

    private val numRecords = AtomicLong()
    private val numRecordBytes = AtomicLong()
    private val buffer: MutableList<ByteArray> = Collections.synchronizedList(ArrayList(1_000_000))

    override fun accept(record: DebeziumRecord) {
        val recordJsonBytes = Jsons.toBytes(record.debeziumEventValue)
        buffer.add(recordJsonBytes)
        numRecords.incrementAndGet()
        numRecordBytes.addAndGet(recordJsonBytes.size.toLong())
        return
    }

    override fun shouldCheckpoint(): Boolean =
        numRecords.get() >= maxRecords || numRecordBytes.get() >= maxRecordBytes

    override fun flush(): Sequence<DebeziumRecord> =
        buffer.asSequence().map { DebeziumRecord(Jsons.deserializeExact(it)) }

    class Builder(
        @JvmField val maxRecords: Long = Long.MAX_VALUE,
        @JvmField val maxRecordBytes: Long = Long.MAX_VALUE,
    ) : ConsumerComponent.Builder<DebeziumRecord> {

        override fun build(): ConsumerComponent<DebeziumRecord> =
            DebeziumConsumer(maxRecords, maxRecordBytes)
    }
}
