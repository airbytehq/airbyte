/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb

import com.google.common.collect.AbstractIterator
import io.airbyte.cdk.db.IncrementalUtils.compareCursors
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import kotlin.jvm.optionals.getOrNull

private val LOGGER = KotlinLogging.logger {}

@Deprecated("")
class StateDecoratingIterator(
    private val messageIterator: Iterator<AirbyteMessage>,
    private val stateManager: StateManager,
    private val pair: AirbyteStreamNameNamespacePair,
    private val cursorField: String,
    private val initialCursor: String,
    private val cursorType: JsonSchemaPrimitiveUtil.JsonSchemaPrimitive,
    stateEmissionFrequency: Int
) : AbstractIterator<AirbyteMessage>(), MutableIterator<AirbyteMessage> {
    private var currentMaxCursor: String?
    private var currentMaxCursorRecordCount = 0L
    private var hasEmittedFinalState = false

    /**
     * These parameters are for intermediate state message emission. We can emit an intermediate
     * state when the following two conditions are met.
     *
     * 1. The records are sorted by the cursor field. This is true when `stateEmissionFrequency` >
     * 0. This logic is guaranteed in `AbstractJdbcSource#queryTableIncremental`, in which an "ORDER
     * BY" clause is appended to the SQL query if `stateEmissionFrequency` > 0.
     *
     * 2. There is a cursor value that is ready for emission. A cursor value is "ready" if there is
     * no more record with the same value. We cannot emit a cursor at will, because there may be
     * multiple records with the same cursor value. If we emit a cursor ignoring this condition,
     * should the sync fail right after the emission, the next sync may skip some records with the
     * same cursor value due to "WHERE cursor_field > cursor" in
     * `AbstractJdbcSource#queryTableIncremental`.
     *
     * The `intermediateStateMessage` is set to the latest state message that is ready for emission.
     * For every `stateEmissionFrequency` messages, `emitIntermediateState` is set to true and the
     * latest "ready" state will be emitted in the next `computeNext` call.
     */
    private val stateEmissionFrequency: Int
    private var totalRecordCount = 0

    // In between each state message, recordCountInStateMessage will be reset to 0.
    private var recordCountInStateMessage = 0
    private var emitIntermediateState = false
    private var intermediateStateMessage: AirbyteMessage? = null
    private var hasCaughtException = false

    /**
     * @param stateManager Manager that maintains connector state
     * @param pair Stream Name and Namespace (e.g. public.users)
     * @param cursorField Path to the comparator field used to track the records read so far
     * @param initialCursor name of the initial cursor column
     * @param cursorType ENUM type of primitive values that can be used as a cursor for
     * checkpointing
     * @param stateEmissionFrequency If larger than 0, the records are sorted by the cursor field,
     * and intermediate states will be emitted for every `stateEmissionFrequency` records. The order
     * of the records is guaranteed in `AbstractJdbcSource#queryTableIncremental`, in which an
     * "ORDER BY" clause is appended to the SQL query if `stateEmissionFrequency` > 0.
     */
    init {
        this.currentMaxCursor = initialCursor
        this.stateEmissionFrequency = stateEmissionFrequency
    }

    private fun getCursorCandidate(message: AirbyteMessage): String? {
        val cursorCandidate = message.record.data[cursorField].asText()
        return (if (cursorCandidate != null) replaceNull(cursorCandidate) else null)
    }

    private fun replaceNull(cursorCandidate: String): String {
        if (cursorCandidate.contains("\u0000")) {
            return cursorCandidate.replace("\u0000".toRegex(), "")
        }
        return cursorCandidate
    }

    /**
     * Computes the next record retrieved from Source stream. Emits StateMessage containing data of
     * the record that has been read so far
     *
     * If this method throws an exception, it will propagate outward to the `hasNext` or `next`
     * invocation that invoked this method. Any further attempts to use the iterator will result in
     * an [IllegalStateException].
     *
     * @return [AirbyteStateMessage] containing information of the records read so far
     */
    override fun computeNext(): AirbyteMessage? {
        if (hasCaughtException) {
            // Mark iterator as done since the next call to messageIterator will result in an
            // IllegalArgumentException and resets exception caught state.
            // This occurs when the previous iteration emitted state so this iteration cycle will
            // indicate
            // iteration is complete
            hasCaughtException = false
            return endOfData()
        }

        if (messageIterator.hasNext()) {
            var optionalIntermediateMessage = intermediateMessage
            if (optionalIntermediateMessage.isPresent) {
                return optionalIntermediateMessage.get()
            }

            totalRecordCount++
            recordCountInStateMessage++
            // Use try-catch to catch Exception that could occur when connection to the database
            // fails
            try {
                val message = messageIterator.next()
                if (message.record.data.hasNonNull(cursorField)) {
                    val cursorCandidate = getCursorCandidate(message)
                    val cursorComparison =
                        compareCursors(currentMaxCursor, cursorCandidate, cursorType)
                    if (cursorComparison < 0) {
                        // Update the current max cursor only when current max cursor < cursor
                        // candidate from the message
                        if (
                            stateEmissionFrequency > 0 &&
                                currentMaxCursor != initialCursor &&
                                messageIterator.hasNext()
                        ) {
                            // Only create an intermediate state when it is not the first or last
                            // record message.
                            // The last state message will be processed seperately.
                            intermediateStateMessage =
                                createStateMessage(false, recordCountInStateMessage)
                        }
                        currentMaxCursor = cursorCandidate
                        currentMaxCursorRecordCount = 1L
                    } else if (cursorComparison == 0) {
                        currentMaxCursorRecordCount++
                    } else if (cursorComparison > 0 && stateEmissionFrequency > 0) {
                        LOGGER.warn {
                            "Intermediate state emission feature requires records to be processed in order according to the cursor value. Otherwise, " +
                                "data loss can occur."
                        }
                    }
                }

                if (stateEmissionFrequency > 0 && totalRecordCount % stateEmissionFrequency == 0) {
                    emitIntermediateState = true
                }

                return message
            } catch (e: Exception) {
                emitIntermediateState = true
                hasCaughtException = true
                LOGGER.error(e) { "Message iterator failed to read next record." }
                optionalIntermediateMessage = intermediateMessage
                return optionalIntermediateMessage.orElse(endOfData())
            }
        } else if (!hasEmittedFinalState) {
            return createStateMessage(true, recordCountInStateMessage)
        } else {
            return endOfData()
        }
    }

    protected val intermediateMessage: Optional<AirbyteMessage>
        /**
         * Returns AirbyteStateMessage when in a ready state, a ready state means that it has
         * satifies the conditions of:
         *
         * cursorField has changed (e.g. 08-22-2022 -> 08-23-2022) and there have been at least
         * stateEmissionFrequency number of records since the last emission
         *
         * @return AirbyteStateMessage if one exists, otherwise Optional indicating state was not
         * ready to be emitted
         */
        get() {
            val message: AirbyteMessage? = intermediateStateMessage
            if (emitIntermediateState && message != null) {
                if (message.state != null) {
                    message.state.sourceStats =
                        AirbyteStateStats().withRecordCount(recordCountInStateMessage.toDouble())
                }

                intermediateStateMessage = null
                recordCountInStateMessage = 0
                emitIntermediateState = false
                return Optional.of(message)
            }
            return Optional.empty()
        }

    /**
     * Creates AirbyteStateMessage while updating the cursor used to checkpoint the state of records
     * read up so far
     *
     * @param isFinalState marker for if the final state of the iterator has been reached
     * @param recordCount count of read messages
     * @return AirbyteMessage which includes information on state of records read so far
     */
    fun createStateMessage(isFinalState: Boolean, recordCount: Int): AirbyteMessage {
        val stateMessage =
            stateManager.updateAndEmit(pair, currentMaxCursor, currentMaxCursorRecordCount)
        val cursorInfo = stateManager.getCursorInfo(pair).getOrNull()

        // logging once every 100 messages to reduce log verbosity
        if (recordCount % 100 == 0) {
            LOGGER.info {
                "State report for stream $pair - original: ${cursorInfo?.originalCursorField} = ${cursorInfo?.originalCursor}" +
                    " (count ${cursorInfo?.originalCursorRecordCount}) -> latest: ${cursorInfo?.cursorField} = " +
                    "${cursorInfo?.cursor} (count ${cursorInfo?.cursorRecordCount})"
            }
        }

        stateMessage?.withSourceStats(AirbyteStateStats().withRecordCount(recordCount.toDouble()))
        if (isFinalState) {
            hasEmittedFinalState = true
            if (stateManager.getCursor(pair).isEmpty) {
                LOGGER.warn {
                    "Cursor for stream $pair was null. This stream will replicate all records on the next run"
                }
            }
        }

        return AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage)
    }
}
