/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.IncrementalUtils.compareCursors
import io.airbyte.cdk.db.IncrementalUtils.getCursorField
import io.airbyte.cdk.db.IncrementalUtils.getCursorType
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*

private val LOGGER = KotlinLogging.logger {}

class CursorStateMessageProducer(
    private val stateManager: StateManager?,
    private val initialCursor: Optional<String>
) : SourceStateMessageProducer<AirbyteMessage> {
    private var currentMaxCursor: Optional<String>

    // We keep this field to mark `cursor_record_count` and also to control logging frequency.
    private var currentCursorRecordCount = 0
    private var intermediateStateMessage: AirbyteStateMessage? = null

    private var cursorOutOfOrderDetected = false

    init {
        this.currentMaxCursor = initialCursor
    }

    override fun generateStateMessageAtCheckpoint(
        stream: ConfiguredAirbyteStream?
    ): AirbyteStateMessage? {
        // At this stage intermediate state message should never be null; otherwise it would have
        // been
        // blocked by shouldEmitStateMessage check.
        val message = intermediateStateMessage
        intermediateStateMessage = null
        if (cursorOutOfOrderDetected) {
            LOGGER.warn {
                "Intermediate state emission feature requires records to be processed in order according to the cursor value. Otherwise, " +
                    "data loss can occur."
            }
        }
        return message
    }

    /**
     * Note: We do not try to catch exception here. If error/exception happens, we should fail the
     * sync, and since we have saved state message before, we should be able to resume it in next
     * sync if we have fixed the underlying issue, of if the issue is transient.
     */
    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun processRecordMessage(
        stream: ConfiguredAirbyteStream?,
        message: AirbyteMessage
    ): AirbyteMessage {
        val cursorField = getCursorField(stream!!)
        if (message.record.data.hasNonNull(cursorField)) {
            val cursorCandidate = getCursorCandidate(cursorField, message)
            val cursorType = getCursorType(stream, cursorField)
            val cursorComparison =
                compareCursors(currentMaxCursor.orElse(null), cursorCandidate, cursorType)
            if (cursorComparison < 0) {
                // Reset cursor but include current record message. This value will be used to
                // create state message.
                // Update the current max cursor only when current max cursor < cursor candidate
                // from the message
                if (currentMaxCursor != initialCursor) {
                    // Only create an intermediate state when it is not the first record.
                    intermediateStateMessage = createStateMessage(stream)
                }
                currentMaxCursor = Optional.of(cursorCandidate!!)
                currentCursorRecordCount = 1
            } else if (cursorComparison > 0) {
                cursorOutOfOrderDetected = true
            } else {
                currentCursorRecordCount++
            }
        }
        return message
    }

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun createFinalStateMessage(stream: ConfiguredAirbyteStream?): AirbyteStateMessage? {
        return createStateMessage(stream!!)
    }

    /** Only sends out state message when there is a state message to be sent out. */
    override fun shouldEmitStateMessage(stream: ConfiguredAirbyteStream?): Boolean {
        return intermediateStateMessage != null
    }

    /**
     * Creates AirbyteStateMessage while updating the cursor used to checkpoint the state of records
     * read up so far
     *
     * @return AirbyteMessage which includes information on state of records read so far
     */
    private fun createStateMessage(stream: ConfiguredAirbyteStream): AirbyteStateMessage? {
        val pair = AirbyteStreamNameNamespacePair(stream.stream.name, stream.stream.namespace)
        val stateMessage =
            stateManager!!.updateAndEmit(
                pair,
                currentMaxCursor.orElse(null),
                currentCursorRecordCount.toLong()
            )
        val cursorInfo = stateManager.getCursorInfo(pair)

        // logging once every 100 messages to reduce log verbosity
        if (currentCursorRecordCount % LOG_FREQUENCY == 0) {
            LOGGER.info { "State report for stream $pair: $cursorInfo" }
        }

        return stateMessage
    }

    private fun getCursorCandidate(cursorField: String, message: AirbyteMessage): String? {
        val cursorCandidate = message.record.data[cursorField].asText()
        return (if (cursorCandidate != null) replaceNull(cursorCandidate) else null)
    }

    private fun replaceNull(cursorCandidate: String): String {
        if (cursorCandidate.contains("\u0000")) {
            return cursorCandidate.replace("\u0000".toRegex(), "")
        }
        return cursorCandidate
    }

    companion object {

        private const val LOG_FREQUENCY = 100
    }
}
