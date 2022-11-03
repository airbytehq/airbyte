/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.tracing;

import static io.airbyte.metrics.lib.ApmTraceConstants.WORKFLOW_TRACE_OPERATION_NAME;
import static io.airbyte.workers.tracing.TemporalSdkInterceptor.ERROR_MESSAGE_TAG_KEY;
import static io.airbyte.workers.tracing.TemporalSdkInterceptor.EXIT_ERROR_MESSAGE;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link TemporalSdkInterceptor} class.
 */
class TemporalSdkInterceptorTest {

  @Test
  void testOnTraceComplete() {
    final var simple = new DummySpan();

    final var noError = new DummySpan();
    noError.setError(false);
    noError.setOperationName(WORKFLOW_TRACE_OPERATION_NAME);
    noError.setTag("tag", "value");

    final var otherError = new DummySpan();
    otherError.setError(true);
    otherError.setOperationName(WORKFLOW_TRACE_OPERATION_NAME);
    otherError.setTag("error.message", "some other error");

    final var temporalExitMsgError = new DummySpan();
    temporalExitMsgError.setError(true);
    temporalExitMsgError.setOperationName(WORKFLOW_TRACE_OPERATION_NAME);
    temporalExitMsgError.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);

    final var temporalExitMsgOtherResourceError = new DummySpan();
    temporalExitMsgOtherResourceError.setError(true);
    temporalExitMsgOtherResourceError.setOperationName("OtherOperation");
    temporalExitMsgOtherResourceError.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);

    final var spans = List.of(
        simple, noError, otherError, temporalExitMsgError, temporalExitMsgOtherResourceError);

    final var interceptor = new TemporalSdkInterceptor();
    final var actual = interceptor.onTraceComplete(spans);

    assertEquals(spans, actual);
    assertFalse(simple.isError());
    assertFalse(noError.isError());
    assertTrue(otherError.isError());
    assertFalse(temporalExitMsgError.isError());
    assertTrue(temporalExitMsgOtherResourceError.isError());
  }

  @Test
  void testIsExitTrace() {
    final var interceptor = new TemporalSdkInterceptor();

    assertEquals(false, interceptor.isExitTrace(null));
    assertEquals(false, interceptor.isExitTrace(new DummySpan()));

    final var temporalTrace = new DummySpan();
    temporalTrace.setOperationName(WORKFLOW_TRACE_OPERATION_NAME);
    assertEquals(false, interceptor.isExitTrace(temporalTrace));

    final var temporalTraceWithError = new DummySpan();
    temporalTraceWithError.setError(true);
    temporalTraceWithError.setOperationName(WORKFLOW_TRACE_OPERATION_NAME);
    assertEquals(false, interceptor.isExitTrace(temporalTraceWithError));

    final var temporalTraceWithExitError = new DummySpan();
    temporalTraceWithExitError.setError(true);
    temporalTraceWithExitError.setOperationName(WORKFLOW_TRACE_OPERATION_NAME);
    temporalTraceWithExitError.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);
    assertEquals(true, interceptor.isExitTrace(temporalTraceWithExitError));

    final var otherTemporalTraceWithExitError = new DummySpan();
    otherTemporalTraceWithExitError.setError(true);
    otherTemporalTraceWithExitError.setOperationName("OtherOperation");
    otherTemporalTraceWithExitError.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);
    assertEquals(false, interceptor.isExitTrace(otherTemporalTraceWithExitError));
  }

  @Test
  void testPriority() {
    final var interceptor = new TemporalSdkInterceptor();
    assertEquals(0, interceptor.priority());
  }

}
