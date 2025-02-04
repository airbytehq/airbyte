/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.JsonValue

import io.airbyte.protocol.models.AirbyteTraceMessage
import org.apache.commons.lang3.exception.ExceptionUtils

object FailureHelper {
    private const val JOB_ID_METADATA_KEY = "jobId"
    private const val ATTEMPT_NUMBER_METADATA_KEY = "attemptNumber"
    private const val TRACE_MESSAGE_METADATA_KEY = "from_trace_message"
    private const val CONNECTOR_COMMAND_METADATA_KEY = "connector_command"

    fun genericFailure(t: Throwable, jobId: Long, attemptNumber: Int): FailureReason {
        return FailureReason()
            .withInternalMessage(t.message)
            .withStacktrace(ExceptionUtils.getStackTrace(t))
            .withTimestamp(System.currentTimeMillis())
            .withMetadata(jobAndAttemptMetadata(jobId, attemptNumber))
    }

    // Generate a FailureReason from an AirbyteTraceMessage.
    // The FailureReason.failureType enum value is taken from the
    // AirbyteErrorTraceMessage.failureType enum value, so the same enum value
    // must exist on both Enums in order to be applied correctly to the FailureReason
    fun genericFailure(m: AirbyteTraceMessage, jobId: Long?, attemptNumber: Int?): FailureReason {
        var failureType: FailureReason.FailureType?
        if (m.error.failureType == null) {
            // default to system_error when no failure type is set
            failureType = FailureReason.FailureType.SYSTEM_ERROR
        } else {
            try {
                val traceMessageError = m.error.failureType.toString()
                failureType = FailureReason.FailureType.fromValue(traceMessageError)
            } catch (e: IllegalArgumentException) {
                // the trace message error does not exist as a FailureReason failure type,
                // so set the failure type to null
                failureType = FailureReason.FailureType.SYSTEM_ERROR
            }
        }
        return FailureReason()
            .withInternalMessage(m.error.internalMessage)
            .withExternalMessage(m.error.message)
            .withStacktrace(m.error.stackTrace)
            .withTimestamp(m.emittedAt.toLong())
            .withFailureType(failureType)
            .withMetadata(traceMessageMetadata(jobId, attemptNumber))
    }

    fun connectorCommandFailure(
        m: AirbyteTraceMessage,
        jobId: Long?,
        attemptNumber: Int?,
        connectorCommand: ConnectorCommand
    ): FailureReason {
        val metadata = traceMessageMetadata(jobId, attemptNumber)
        metadata.withAdditionalProperty(CONNECTOR_COMMAND_METADATA_KEY, connectorCommand.toString())
        return genericFailure(m, jobId, attemptNumber).withMetadata(metadata)
    }

    fun connectorCommandFailure(
        t: Throwable,
        jobId: Long,
        attemptNumber: Int,
        connectorCommand: ConnectorCommand
    ): FailureReason {
        val metadata = jobAndAttemptMetadata(jobId, attemptNumber)
        metadata.withAdditionalProperty(CONNECTOR_COMMAND_METADATA_KEY, connectorCommand.toString())
        return genericFailure(t, jobId, attemptNumber).withMetadata(metadata)
    }

    fun sourceFailure(t: Throwable, jobId: Long, attemptNumber: Int): FailureReason {
        return connectorCommandFailure(t, jobId, attemptNumber, ConnectorCommand.READ)
            .withFailureOrigin(FailureReason.FailureOrigin.SOURCE)
            .withExternalMessage("Something went wrong within the source connector")
    }

    fun sourceFailure(m: AirbyteTraceMessage, jobId: Long?, attemptNumber: Int?): FailureReason {
        return connectorCommandFailure(m, jobId, attemptNumber, ConnectorCommand.READ)
            .withFailureOrigin(FailureReason.FailureOrigin.SOURCE)
    }

    fun destinationFailure(t: Throwable, jobId: Long, attemptNumber: Int): FailureReason {
        return connectorCommandFailure(t, jobId, attemptNumber, ConnectorCommand.WRITE)
            .withFailureOrigin(FailureReason.FailureOrigin.DESTINATION)
            .withExternalMessage("Something went wrong within the destination connector")
    }

    fun destinationFailure(
        m: AirbyteTraceMessage,
        jobId: Long?,
        attemptNumber: Int?
    ): FailureReason {
        return connectorCommandFailure(m, jobId, attemptNumber, ConnectorCommand.WRITE)
            .withFailureOrigin(FailureReason.FailureOrigin.DESTINATION)
    }

    fun checkFailure(
        t: Throwable,
        jobId: Long,
        attemptNumber: Int,
        origin: FailureReason.FailureOrigin?
    ): FailureReason {
        return connectorCommandFailure(t, jobId, attemptNumber, ConnectorCommand.CHECK)
            .withFailureOrigin(origin)
            .withFailureType(FailureReason.FailureType.CONFIG_ERROR)
            .withRetryable(false)
            .withExternalMessage(
                String.format(
                    "Checking %s connection failed - please review this connection's configuration to prevent future syncs from failing",
                    origin
                )
            )
    }

    fun unknownOriginFailure(t: Throwable, jobId: Long, attemptNumber: Int): FailureReason {
        return genericFailure(t, jobId, attemptNumber)
            .withFailureOrigin(FailureReason.FailureOrigin.UNKNOWN)
            .withExternalMessage("An unknown failure occurred")
    }

    private fun jobAndAttemptMetadata(jobId: Long, attemptNumber: Int): Metadata {
        return Metadata()
            .withAdditionalProperty(JOB_ID_METADATA_KEY, jobId)
            .withAdditionalProperty(ATTEMPT_NUMBER_METADATA_KEY, attemptNumber)
    }

    private fun traceMessageMetadata(jobId: Long?, attemptNumber: Int?): Metadata {
        return Metadata()
            .withAdditionalProperty(JOB_ID_METADATA_KEY, jobId)
            .withAdditionalProperty(ATTEMPT_NUMBER_METADATA_KEY, attemptNumber)
            .withAdditionalProperty(TRACE_MESSAGE_METADATA_KEY, true)
    }

    /**
     * Orders failures by putting errors from trace messages first, and then orders by timestamp, so
     * that earlier failures come first.
     */
    fun orderedFailures(failures: Set<FailureReason>): List<FailureReason> {
        val compareByIsTrace =
            Comparator.comparing { failureReason: FailureReason ->
                val metadata: Any? = failureReason.metadata
                if (metadata != null) {
                    return@comparing if (
                        failureReason.metadata!!.additionalProperties.containsKey(
                            TRACE_MESSAGE_METADATA_KEY
                        )
                    )
                        0
                    else 1
                } else {
                    return@comparing 1
                }
            }
        val compareByTimestamp = Comparator.comparing { obj: FailureReason -> obj.timestamp!! }
        val compareByTraceAndTimestamp = compareByIsTrace.thenComparing(compareByTimestamp)
        return failures.sortedWith(compareByTraceAndTimestamp)
    }

    enum class ConnectorCommand(private val value: String) {
        SPEC("spec"),
        CHECK("check"),
        DISCOVER("discover"),
        WRITE("write"),
        READ("read");

        @JsonValue
        override fun toString(): String {
            return value.toString()
        }
    }
}
