/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.helper

import io.airbyte.configoss.FailureReason
import io.airbyte.configoss.Metadata
import io.airbyte.protocol.models.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.AirbyteTraceMessage
import io.airbyte.workers.test_utils.AirbyteMessageUtils
import java.util.Set
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class FailureHelperTest {
    @Test
    @Throws(Exception::class)
    fun testGenericFailureFromTrace() {
        val traceMessage =
            AirbyteMessageUtils.createErrorTraceMessage(
                "trace message error",
                123.0,
                AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR
            )
        val failureReason = FailureHelper.genericFailure(traceMessage, 12345, 1)
        Assertions.assertEquals(FailureReason.FailureType.CONFIG_ERROR, failureReason.failureType)
    }

    @Test
    @Throws(Exception::class)
    fun testGenericFailureFromTraceNoFailureType() {
        val failureReason = FailureHelper.genericFailure(TRACE_MESSAGE, 12345, 1)
        Assertions.assertEquals(failureReason.failureType, FailureReason.FailureType.SYSTEM_ERROR)
    }

    @Test
    fun testConnectorCommandFailure() {
        val t: Throwable = RuntimeException()
        val jobId = 12345L
        val attemptNumber = 1
        val failureReason =
            FailureHelper.connectorCommandFailure(
                t,
                jobId,
                attemptNumber,
                FailureHelper.ConnectorCommand.CHECK
            )

        val metadata = failureReason.metadata.additionalProperties
        Assertions.assertEquals("check", metadata[CONNECTOR_COMMAND_KEY])
        Assertions.assertNull(metadata[FROM_TRACE_MESSAGE_KEY])
        Assertions.assertEquals(jobId, metadata[JOB_ID_KEY])
        Assertions.assertEquals(attemptNumber, metadata[ATTEMPT_NUMBER_KEY])
    }

    @Test
    fun testConnectorCommandFailureFromTrace() {
        val jobId = 12345L
        val attemptNumber = 1
        val failureReason =
            FailureHelper.connectorCommandFailure(
                TRACE_MESSAGE,
                jobId,
                attemptNumber,
                FailureHelper.ConnectorCommand.DISCOVER
            )

        val metadata = failureReason.metadata.additionalProperties
        Assertions.assertEquals("discover", metadata[CONNECTOR_COMMAND_KEY])
        Assertions.assertEquals(true, metadata[FROM_TRACE_MESSAGE_KEY])
        Assertions.assertEquals(jobId, metadata[JOB_ID_KEY])
        Assertions.assertEquals(attemptNumber, metadata[ATTEMPT_NUMBER_KEY])
    }

    @Test
    fun testSourceFailure() {
        val t: Throwable = RuntimeException()
        val jobId = 12345L
        val attemptNumber = 1
        val failureReason = FailureHelper.sourceFailure(t, jobId, attemptNumber)
        Assertions.assertEquals(FailureReason.FailureOrigin.SOURCE, failureReason.failureOrigin)

        val metadata = failureReason.metadata.additionalProperties
        Assertions.assertEquals("read", metadata[CONNECTOR_COMMAND_KEY])
        Assertions.assertNull(metadata[FROM_TRACE_MESSAGE_KEY])
        Assertions.assertEquals(jobId, metadata[JOB_ID_KEY])
        Assertions.assertEquals(attemptNumber, metadata[ATTEMPT_NUMBER_KEY])
    }

    @Test
    fun testSourceFailureFromTrace() {
        val jobId = 12345L
        val attemptNumber = 1
        val failureReason = FailureHelper.sourceFailure(TRACE_MESSAGE, jobId, attemptNumber)
        Assertions.assertEquals(FailureReason.FailureOrigin.SOURCE, failureReason.failureOrigin)

        val metadata = failureReason.metadata.additionalProperties
        Assertions.assertEquals("read", metadata[CONNECTOR_COMMAND_KEY])
        Assertions.assertEquals(true, metadata[FROM_TRACE_MESSAGE_KEY])
        Assertions.assertEquals(jobId, metadata[JOB_ID_KEY])
        Assertions.assertEquals(attemptNumber, metadata[ATTEMPT_NUMBER_KEY])
    }

    @Test
    fun testDestinationFailure() {
        val t: Throwable = RuntimeException()
        val jobId = 12345L
        val attemptNumber = 1
        val failureReason = FailureHelper.destinationFailure(t, jobId, attemptNumber)
        Assertions.assertEquals(
            FailureReason.FailureOrigin.DESTINATION,
            failureReason.failureOrigin
        )

        val metadata = failureReason.metadata.additionalProperties
        Assertions.assertEquals("write", metadata[CONNECTOR_COMMAND_KEY])
        Assertions.assertNull(metadata[FROM_TRACE_MESSAGE_KEY])
        Assertions.assertEquals(jobId, metadata[JOB_ID_KEY])
        Assertions.assertEquals(attemptNumber, metadata[ATTEMPT_NUMBER_KEY])
    }

    @Test
    fun testDestinationFailureFromTrace() {
        val jobId = 12345L
        val attemptNumber = 1
        val failureReason = FailureHelper.destinationFailure(TRACE_MESSAGE, jobId, attemptNumber)
        Assertions.assertEquals(
            FailureReason.FailureOrigin.DESTINATION,
            failureReason.failureOrigin
        )

        val metadata = failureReason.metadata.additionalProperties
        Assertions.assertEquals("write", metadata[CONNECTOR_COMMAND_KEY])
        Assertions.assertEquals(true, metadata[FROM_TRACE_MESSAGE_KEY])
        Assertions.assertEquals(jobId, metadata[JOB_ID_KEY])
        Assertions.assertEquals(attemptNumber, metadata[ATTEMPT_NUMBER_KEY])
    }

    @Test
    fun testCheckFailure() {
        val t: Throwable = RuntimeException()
        val jobId = 12345L
        val attemptNumber = 1
        val failureReason =
            FailureHelper.checkFailure(
                t,
                jobId,
                attemptNumber,
                FailureReason.FailureOrigin.DESTINATION
            )
        Assertions.assertEquals(
            FailureReason.FailureOrigin.DESTINATION,
            failureReason.failureOrigin
        )

        val metadata = failureReason.metadata.additionalProperties
        Assertions.assertEquals("check", metadata[CONNECTOR_COMMAND_KEY])
        Assertions.assertNull(metadata[FROM_TRACE_MESSAGE_KEY])
        Assertions.assertEquals(jobId, metadata[JOB_ID_KEY])
        Assertions.assertEquals(attemptNumber, metadata[ATTEMPT_NUMBER_KEY])
    }

    @Test
    @Throws(Exception::class)
    fun testOrderedFailures() {
        val failureReasonList =
            FailureHelper.orderedFailures(
                Set.of(TRACE_FAILURE_REASON_2, TRACE_FAILURE_REASON, EXCEPTION_FAILURE_REASON)
            )
        Assertions.assertEquals(failureReasonList[0], TRACE_FAILURE_REASON)
    }

    @Test
    fun testUnknownOriginFailure() {
        val t: Throwable = RuntimeException()
        val jobId = 12345L
        val attemptNumber = 1
        val failureReason = FailureHelper.unknownOriginFailure(t, jobId, attemptNumber)
        Assertions.assertEquals(FailureReason.FailureOrigin.UNKNOWN, failureReason.failureOrigin)
        Assertions.assertEquals("An unknown failure occurred", failureReason.externalMessage)
    }

    companion object {
        private const val FROM_TRACE_MESSAGE_KEY = "from_trace_message"
        private const val CONNECTOR_COMMAND_KEY = "connector_command"
        private const val JOB_ID_KEY = "jobId"
        private const val ATTEMPT_NUMBER_KEY = "attemptNumber"

        private val TRACE_FAILURE_REASON: FailureReason =
            FailureReason()
                .withInternalMessage("internal message")
                .withStacktrace("stack trace")
                .withTimestamp(1111112)
                .withMetadata(
                    Metadata()
                        .withAdditionalProperty(JOB_ID_KEY, 12345)
                        .withAdditionalProperty(ATTEMPT_NUMBER_KEY, 1)
                        .withAdditionalProperty(FROM_TRACE_MESSAGE_KEY, true)
                )

        private val TRACE_FAILURE_REASON_2: FailureReason =
            FailureReason()
                .withInternalMessage("internal message")
                .withStacktrace("stack trace")
                .withTimestamp(1111113)
                .withMetadata(
                    Metadata()
                        .withAdditionalProperty(JOB_ID_KEY, 12345)
                        .withAdditionalProperty(ATTEMPT_NUMBER_KEY, 1)
                        .withAdditionalProperty(FROM_TRACE_MESSAGE_KEY, true)
                )

        private val EXCEPTION_FAILURE_REASON: FailureReason =
            FailureReason()
                .withInternalMessage("internal message")
                .withStacktrace("stack trace")
                .withTimestamp(1111111)
                .withMetadata(
                    Metadata()
                        .withAdditionalProperty(JOB_ID_KEY, 12345)
                        .withAdditionalProperty(ATTEMPT_NUMBER_KEY, 1)
                )

        private val TRACE_MESSAGE: AirbyteTraceMessage =
            AirbyteMessageUtils.createErrorTraceMessage(
                "trace message error",
                123.0,
                AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR
            )
    }
}
