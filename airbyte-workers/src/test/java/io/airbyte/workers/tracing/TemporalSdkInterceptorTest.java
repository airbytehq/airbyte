/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.tracing;

import static io.airbyte.metrics.lib.ApmTraceConstants.WORKFLOW_TRACE_OPERATION_NAME;
import static io.airbyte.workers.tracing.TemporalSdkInterceptor.CONNECTION_MANAGER_WORKFLOW_IMPL_RESOURCE_NAME;
import static io.airbyte.workers.tracing.TemporalSdkInterceptor.ERROR_MESSAGE_TAG_KEY;
import static io.airbyte.workers.tracing.TemporalSdkInterceptor.EXIT_ERROR_MESSAGE;
import static io.airbyte.workers.tracing.TemporalSdkInterceptor.SYNC_WORKFLOW_IMPL_RESOURCE_NAME;
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
    otherError.setTag(ERROR_MESSAGE_TAG_KEY, "some other error");

    final var temporalExitMsgOperationNameError = new DummySpan();
    temporalExitMsgOperationNameError.setError(true);
    temporalExitMsgOperationNameError.setOperationName(WORKFLOW_TRACE_OPERATION_NAME);
    temporalExitMsgOperationNameError.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);

    final var connectionManagerTemporalExitMsgResourceNameError = new DummySpan();
    connectionManagerTemporalExitMsgResourceNameError.setError(true);
    connectionManagerTemporalExitMsgResourceNameError.setResourceName(CONNECTION_MANAGER_WORKFLOW_IMPL_RESOURCE_NAME);
    connectionManagerTemporalExitMsgResourceNameError.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);

    final var syncWorkflowTemporalExitMsgResourceNameError = new DummySpan();
    syncWorkflowTemporalExitMsgResourceNameError.setError(true);
    syncWorkflowTemporalExitMsgResourceNameError.setResourceName(SYNC_WORKFLOW_IMPL_RESOURCE_NAME);
    syncWorkflowTemporalExitMsgResourceNameError.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);

    final var temporalExitMsgOtherOperationError = new DummySpan();
    temporalExitMsgOtherOperationError.setError(true);
    temporalExitMsgOtherOperationError.setOperationName("OtherOperation");
    temporalExitMsgOtherOperationError.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);

    final var temporalExitMsgOtherResourceError = new DummySpan();
    temporalExitMsgOtherResourceError.setError(true);
    temporalExitMsgOtherResourceError.setResourceName("OtherResource");
    temporalExitMsgOtherResourceError.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);

    final var spans = List.of(
        simple, noError, otherError, temporalExitMsgOperationNameError, connectionManagerTemporalExitMsgResourceNameError,
        syncWorkflowTemporalExitMsgResourceNameError, temporalExitMsgOtherOperationError,
        temporalExitMsgOtherResourceError);

    final var interceptor = new TemporalSdkInterceptor();
    final var actual = interceptor.onTraceComplete(spans);

    assertEquals(spans, actual);
    assertFalse(simple.isError());
    assertFalse(noError.isError());
    assertTrue(otherError.isError());
    assertFalse(temporalExitMsgOperationNameError.isError());
    assertFalse(connectionManagerTemporalExitMsgResourceNameError.isError());
    assertFalse(syncWorkflowTemporalExitMsgResourceNameError.isError());
    assertTrue(temporalExitMsgOtherOperationError.isError());
    assertTrue(temporalExitMsgOtherResourceError.isError());
  }

  @Test
  void testIsExitTrace() {
    final var interceptor = new TemporalSdkInterceptor();

    assertEquals(false, interceptor.isExitTrace(null));
    assertEquals(false, interceptor.isExitTrace(new DummySpan()));

    final var temporalTraceWithOperationName = new DummySpan();
    temporalTraceWithOperationName.setOperationName(WORKFLOW_TRACE_OPERATION_NAME);
    assertEquals(false, interceptor.isExitTrace(temporalTraceWithOperationName));

    final var temporalTraceWithResourceName = new DummySpan();
    temporalTraceWithResourceName.setResourceName(CONNECTION_MANAGER_WORKFLOW_IMPL_RESOURCE_NAME);
    assertEquals(false, interceptor.isExitTrace(temporalTraceWithResourceName));

    final var temporalTraceWithErrorAndOperationName = new DummySpan();
    temporalTraceWithErrorAndOperationName.setError(true);
    temporalTraceWithErrorAndOperationName.setOperationName(WORKFLOW_TRACE_OPERATION_NAME);
    assertEquals(false, interceptor.isExitTrace(temporalTraceWithErrorAndOperationName));

    final var temporalTraceWithErrorAndConnectionManagerResourceName = new DummySpan();
    temporalTraceWithErrorAndConnectionManagerResourceName.setError(true);
    temporalTraceWithErrorAndConnectionManagerResourceName.setResourceName(CONNECTION_MANAGER_WORKFLOW_IMPL_RESOURCE_NAME);
    assertEquals(false, interceptor.isExitTrace(temporalTraceWithErrorAndConnectionManagerResourceName));

    final var temporalTraceWithErrorAndSyncWorkflowResourceName = new DummySpan();
    temporalTraceWithErrorAndSyncWorkflowResourceName.setError(true);
    temporalTraceWithErrorAndSyncWorkflowResourceName.setResourceName(SYNC_WORKFLOW_IMPL_RESOURCE_NAME);
    assertEquals(false, interceptor.isExitTrace(temporalTraceWithErrorAndSyncWorkflowResourceName));

    final var temporalTraceWithExitErrorAndOperationName = new DummySpan();
    temporalTraceWithExitErrorAndOperationName.setError(true);
    temporalTraceWithExitErrorAndOperationName.setOperationName(WORKFLOW_TRACE_OPERATION_NAME);
    temporalTraceWithExitErrorAndOperationName.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);
    assertEquals(true, interceptor.isExitTrace(temporalTraceWithExitErrorAndOperationName));

    final var temporalTraceWithExitErrorAndResourceName = new DummySpan();
    temporalTraceWithExitErrorAndResourceName.setError(true);
    temporalTraceWithExitErrorAndResourceName.setResourceName(CONNECTION_MANAGER_WORKFLOW_IMPL_RESOURCE_NAME);
    temporalTraceWithExitErrorAndResourceName.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);
    assertEquals(true, interceptor.isExitTrace(temporalTraceWithExitErrorAndResourceName));

    final var otherTemporalTraceWithExitErrorAndOtherOperationName = new DummySpan();
    otherTemporalTraceWithExitErrorAndOtherOperationName.setError(true);
    otherTemporalTraceWithExitErrorAndOtherOperationName.setOperationName("OtherOperation");
    otherTemporalTraceWithExitErrorAndOtherOperationName.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);
    assertEquals(false, interceptor.isExitTrace(otherTemporalTraceWithExitErrorAndOtherOperationName));

    final var otherTemporalTraceWithExitErrorAndOtherResourceName = new DummySpan();
    otherTemporalTraceWithExitErrorAndOtherResourceName.setError(true);
    otherTemporalTraceWithExitErrorAndOtherResourceName.setResourceName("OtherResource");
    otherTemporalTraceWithExitErrorAndOtherResourceName.setTag(ERROR_MESSAGE_TAG_KEY, EXIT_ERROR_MESSAGE);
    assertEquals(false, interceptor.isExitTrace(otherTemporalTraceWithExitErrorAndOtherResourceName));
  }

  @Test
  void testPriority() {
    final var interceptor = new TemporalSdkInterceptor();
    assertEquals(0, interceptor.priority());
  }

}
