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

    override fun accumulateRecords(
        stream: Stream,
        accumulatorId: Int,
        records: Iterable<DestinationRecord>,
        endOfStream: Boolean,
        forceFlush: Boolean
    ): Batch? {
        log.info { "MockDestination::accumulateRecords($stream, $accumulatorId, eos=$endOfStream, flush=$forceFlush)" }
        var count = accumulatedRecords.getOrPut(stream to accumulatorId) { 0 }
        var processed = 0
        records.forEach {
             processed += 1
            count += 1
            log.info { "MockDestination::accumulateRecords($stream, $accumulatorId): accumulating record $processed(of $count total for this batch): $it" }
        }

        accumulatedRecords[stream to accumulatorId] = count
        if (count % batchEvery == 0 || endOfStream || forceFlush) {
            accumulatedRecords.remove(stream to accumulatorId)
            val batchIndex = batchIndex.getAndIncrement()
            log.info { "Mockdestination::accumulateRecords($stream, $accumulatorId): emitting batch($batchIndex) of size $count" }
            return BatchStage1(batchIndex, "batch($batchIndex) of $count records")
        }

        log.info { "MockDestination::accumulateRecords($stream, $accumulatorId): not emitting batch (${count % batchEvery} / $batchEvery threshold)" }
        return null
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
