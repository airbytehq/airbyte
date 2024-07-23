/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import com.google.common.collect.AbstractIterator
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.time.Instant
import java.time.OffsetDateTime

private val LOGGER = KotlinLogging.logger {}

open class SourceStateIterator<T>(
    private val messageIterator: Iterator<T>,
    private val stream: ConfiguredAirbyteStream?,
    private val sourceStateMessageProducer: SourceStateMessageProducer<T>,
    private val stateEmitFrequency: StateEmitFrequency
) : AbstractIterator<AirbyteMessage>(), MutableIterator<AirbyteMessage> {
    private var hasEmittedFinalState = false
    private var recordCount = 0L
    private var lastCheckpoint: Instant = Instant.now()

    override fun computeNext(): AirbyteMessage? {
        var iteratorHasNextValue: Boolean
        try {
            iteratorHasNextValue = messageIterator.hasNext()
        } catch (ex: Exception) {
            // If the underlying iterator throws an exception, we want to fail the sync, expecting
            // sync/attempt
            // will be restarted and
            // sync will resume from the last state message.
            throw FailedRecordIteratorException(ex)
        }
        if (iteratorHasNextValue) {
            if (
                shouldEmitStateMessage() &&
                    sourceStateMessageProducer.shouldEmitStateMessage(stream)
            ) {
                val stateMessage =
                    sourceStateMessageProducer.generateStateMessageAtCheckpoint(stream)
                stateMessage!!.withSourceStats(
                    AirbyteStateStats().withRecordCount(recordCount.toDouble())
                )

                recordCount = 0L
                lastCheckpoint = Instant.now()
                return AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage)
            }
            // Use try-catch to catch Exception that could occur when connection to the database
            // fails
            try {
                val message = messageIterator.next()
                val processedMessage =
                    sourceStateMessageProducer.processRecordMessage(stream, message)
                recordCount++
                return processedMessage
            } catch (e: Exception) {
                throw FailedRecordIteratorException(e)
            }
        } else if (!hasEmittedFinalState) {
            hasEmittedFinalState = true
            val finalStateMessageForStream =
                sourceStateMessageProducer.createFinalStateMessage(stream)
            finalStateMessageForStream!!.withSourceStats(
                AirbyteStateStats().withRecordCount(recordCount.toDouble())
            )

            recordCount = 0L
            return AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(finalStateMessageForStream)
        } else {
            return endOfData()
        }
    }

    // This method is used to check if we should emit a state message. If the record count is set to
    // 0,
    // we should not emit a state message.
    // If the frequency is set to be zero, we should not use it.
    private fun shouldEmitStateMessage(): Boolean {
        if (stateEmitFrequency.syncCheckpointRecords == 0L) {
            return false
        }
        if (recordCount >= stateEmitFrequency.syncCheckpointRecords) {
            return true
        }
        if (!stateEmitFrequency.syncCheckpointDuration.isZero) {
            return Duration.between(lastCheckpoint, OffsetDateTime.now())
                .compareTo(stateEmitFrequency.syncCheckpointDuration) > 0
        }
        return false
    }

    companion object {}
}
