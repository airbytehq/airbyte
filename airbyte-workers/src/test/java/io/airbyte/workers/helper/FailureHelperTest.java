/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.FailureReason.FailureType;
import io.airbyte.config.Metadata;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import io.airbyte.workers.helper.FailureHelper.ConnectorCommand;
import io.airbyte.workers.internal.AirbyteMessageUtils;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Test;

class FailureHelperTest {

  private static final FailureReason TRACE_FAILURE_REASON = new FailureReason()
      .withInternalMessage("internal message")
      .withStacktrace("stack trace")
      .withTimestamp(Long.valueOf(1111112))
      .withMetadata(new Metadata()
          .withAdditionalProperty("jobId", 12345)
          .withAdditionalProperty("attempt", 1)
          .withAdditionalProperty("from_trace_message", true));

  private static final FailureReason TRACE_FAILURE_REASON_2 = new FailureReason()
      .withInternalMessage("internal message")
      .withStacktrace("stack trace")
      .withTimestamp(Long.valueOf(1111113))
      .withMetadata(new Metadata()
          .withAdditionalProperty("jobId", 12345)
          .withAdditionalProperty("attempt", 1)
          .withAdditionalProperty("from_trace_message", true));

  private static final FailureReason EXCEPTION_FAILURE_REASON = new FailureReason()
      .withInternalMessage("internal message")
      .withStacktrace("stack trace")
      .withTimestamp(Long.valueOf(1111111))
      .withMetadata(new Metadata()
          .withAdditionalProperty("jobId", 12345)
          .withAdditionalProperty("attempt", 1));

  @Test
  void testGenericFailureFromTrace() throws Exception {
    final AirbyteTraceMessage traceMessage = AirbyteMessageUtils.createErrorTraceMessage("trace message error", Double.valueOf(123),
        AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR);
    final FailureReason failureReason = FailureHelper.genericFailure(traceMessage, Long.valueOf(12345), 1);
    assertEquals(FailureType.CONFIG_ERROR, failureReason.getFailureType());
  }

  @Test
  void testGenericFailureFromTraceNoFailureType() throws Exception {
    final AirbyteTraceMessage traceMessage = AirbyteMessageUtils.createErrorTraceMessage("trace message error", Double.valueOf(123));
    final FailureReason failureReason = FailureHelper.genericFailure(traceMessage, Long.valueOf(12345), 1);
    assertEquals(failureReason.getFailureType(), FailureType.SYSTEM_ERROR);
  }

  @Test
  void testConnectorCommandFailure() {
    final Throwable t = new RuntimeException();
    final Long jobId = 12345L;
    final Integer attemptNumber = 1;
    final FailureReason failureReason = FailureHelper.connectorCommandFailure(t, jobId, attemptNumber, ConnectorCommand.CHECK);

    final Map<String, Object> metadata = failureReason.getMetadata().getAdditionalProperties();
    assertEquals("check", metadata.get("connector_command"));
    assertNull(metadata.get("from_trace_message"));
    assertEquals(jobId, metadata.get("jobId"));
    assertEquals(attemptNumber, metadata.get("attemptNumber"));
  }

  @Test
  void testConnectorCommandFailureFromTrace() {
    final AirbyteTraceMessage traceMessage = AirbyteMessageUtils.createErrorTraceMessage("trace message error", Double.valueOf(123),
        AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR);
    final Long jobId = 12345L;
    final Integer attemptNumber = 1;
    final FailureReason failureReason = FailureHelper.connectorCommandFailure(traceMessage, jobId, attemptNumber, ConnectorCommand.DISCOVER);

    final Map<String, Object> metadata = failureReason.getMetadata().getAdditionalProperties();
    assertEquals("discover", metadata.get("connector_command"));
    assertEquals(true, metadata.get("from_trace_message"));
    assertEquals(jobId, metadata.get("jobId"));
    assertEquals(attemptNumber, metadata.get("attemptNumber"));
  }

  @Test
  void testSourceFailure() {
    final Throwable t = new RuntimeException();
    final Long jobId = 12345L;
    final Integer attemptNumber = 1;
    final FailureReason failureReason = FailureHelper.sourceFailure(t, jobId, attemptNumber);
    assertEquals(FailureOrigin.SOURCE, failureReason.getFailureOrigin());

    final Map<String, Object> metadata = failureReason.getMetadata().getAdditionalProperties();
    assertEquals("read", metadata.get("connector_command"));
    assertNull(metadata.get("from_trace_message"));
    assertEquals(jobId, metadata.get("jobId"));
    assertEquals(attemptNumber, metadata.get("attemptNumber"));
  }

  @Test
  void testSourceFailureFromTrace() {
    final AirbyteTraceMessage traceMessage = AirbyteMessageUtils.createErrorTraceMessage("trace message error", Double.valueOf(123),
        AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR);
    final Long jobId = 12345L;
    final Integer attemptNumber = 1;
    final FailureReason failureReason = FailureHelper.sourceFailure(traceMessage, jobId, attemptNumber);
    assertEquals(FailureOrigin.SOURCE, failureReason.getFailureOrigin());

    final Map<String, Object> metadata = failureReason.getMetadata().getAdditionalProperties();
    assertEquals("read", metadata.get("connector_command"));
    assertEquals(true, metadata.get("from_trace_message"));
    assertEquals(jobId, metadata.get("jobId"));
    assertEquals(attemptNumber, metadata.get("attemptNumber"));
  }

  @Test
  void testDestinationFailure() {
    final Throwable t = new RuntimeException();
    final Long jobId = 12345L;
    final Integer attemptNumber = 1;
    final FailureReason failureReason = FailureHelper.destinationFailure(t, jobId, attemptNumber);
    assertEquals(FailureOrigin.DESTINATION, failureReason.getFailureOrigin());

    final Map<String, Object> metadata = failureReason.getMetadata().getAdditionalProperties();
    assertEquals("write", metadata.get("connector_command"));
    assertNull(metadata.get("from_trace_message"));
    assertEquals(jobId, metadata.get("jobId"));
    assertEquals(attemptNumber, metadata.get("attemptNumber"));
  }

  @Test
  void testDestinationFailureFromTrace() {
    final AirbyteTraceMessage traceMessage = AirbyteMessageUtils.createErrorTraceMessage("trace message error", Double.valueOf(123),
        AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR);
    final Long jobId = 12345L;
    final Integer attemptNumber = 1;
    final FailureReason failureReason = FailureHelper.destinationFailure(traceMessage, jobId, attemptNumber);
    assertEquals(FailureOrigin.DESTINATION, failureReason.getFailureOrigin());

    final Map<String, Object> metadata = failureReason.getMetadata().getAdditionalProperties();
    assertEquals("write", metadata.get("connector_command"));
    assertEquals(true, metadata.get("from_trace_message"));
    assertEquals(jobId, metadata.get("jobId"));
    assertEquals(attemptNumber, metadata.get("attemptNumber"));
  }

  @Test
  void testCheckFailure() {
    final Throwable t = new RuntimeException();
    final Long jobId = 12345L;
    final Integer attemptNumber = 1;
    final FailureReason failureReason = FailureHelper.checkFailure(t, jobId, attemptNumber, FailureOrigin.DESTINATION);
    assertEquals(FailureOrigin.DESTINATION, failureReason.getFailureOrigin());

    final Map<String, Object> metadata = failureReason.getMetadata().getAdditionalProperties();
    assertEquals("check", metadata.get("connector_command"));
    assertNull(metadata.get("from_trace_message"));
    assertEquals(jobId, metadata.get("jobId"));
    assertEquals(attemptNumber, metadata.get("attemptNumber"));
  }

  @Test
  void testOrderedFailures() throws Exception {
    final List<FailureReason> failureReasonList =
        FailureHelper.orderedFailures(Set.of(TRACE_FAILURE_REASON_2, TRACE_FAILURE_REASON, EXCEPTION_FAILURE_REASON));
    assertEquals(failureReasonList.get(0), TRACE_FAILURE_REASON);
  }

}
