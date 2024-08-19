package io.airbyte.cdk.write

import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger

class MockDestination(
    private val batchEvery: Int
): StandardDestination() {
    class BatchStage1(
        val index: Int,
        name: String,
        persisted: Boolean = false
    ): Batch(name, persisted)

    class BatchStage2(
        val index: Int,
        name: String,
        persisted: Boolean = false
    ): Batch(name, persisted)

    val log = KotlinLogging.logger {}

    private val accumulatedRecords: ConcurrentHashMap<Pair<Stream, Int>, Int> = ConcurrentHashMap()
    private val batchIndex: AtomicInteger = AtomicInteger(0)

    override fun setup() {
        log.info { "MockDestination::setup" }
    }

    override fun openStream(stream: Stream) {
        log.info { "MockDestination::openStream($stream)" }
    }

    override fun getRecordAccumulator(
        stream: Stream,
        shard: Int
    ): (DestinationMessage.DestinationRecord) -> Batch? {
        var processed = 0
        val count = accumulatedRecords.getOrPut(stream to shard) { 0 }
        return { record ->
            log.info { "MockDestination::accumulateRecords($stream, $shard)" }
            processed += 1
            count.inc()
            log.info { "MockDestination::accumulateRecords($stream, $shard): accumulating record $processed(of $count total for this batch): $record" }
            if (count % batchEvery == 0) {
                accumulatedRecords.remove(stream to shard)
                val batchIndex = batchIndex.getAndIncrement()
                log.info { "Mockdestination::accumulateRecords($stream, $shard): emitting batch($batchIndex) of size $count" }
                BatchStage1(batchIndex, "batch($batchIndex) of $count records")
            } else {
                null
            }
        }
    }

    override fun flush(stream: Stream, endOfStream: Boolean): Batch? {
        log.info { "MockDestination::flush($stream, $endOfStream)" }
        val shardCounts = accumulatedRecords.filterKeys { it.first == stream }.values.sum()
        if (shardCounts > 0) {
            val batchIndex = batchIndex.getAndIncrement()
            log.info { "MockDestination::flush($stream, $endOfStream): emitting batch($batchIndex) of size $shardCounts" }
            return BatchStage1(batchIndex, "batch($batchIndex) of $shardCounts records")
        } else {
            return null
        }
    }

    override fun processBatch(stream: Stream, batch: Batch): Batch? {
        when (batch) {
            is BatchStage1 -> {
                log.info { "MockDestination::processBatch($stream, $batch): processing batch stage1 -> stage2 (persisted)" }
                return BatchStage2(batch.index,"processed ${batch.name}", persisted = true)
            }
            is BatchStage2 -> {
                log.info { "MockDestination::processBatch($stream, $batch): processing batch stage2 -> complete" }
                return null
            }
            else -> {
                throw IllegalArgumentException("Unexpected batch type: $batch")
            }
        }
    }

    override fun closeStream(stream: Stream, succeeded: Boolean) {
        log.info { "MockDestination::closeStream($stream, $succeeded)" }
    }

    override fun teardown(succeeded: Boolean) {
        log.info { "MockDestination::teardown($succeeded)" }
    }
}
