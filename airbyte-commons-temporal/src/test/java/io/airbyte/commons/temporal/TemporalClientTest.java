/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.temporal.scheduling.ConnectionManagerWorkflow;
import io.temporal.api.enums.v1.WorkflowExecutionStatus;
import io.temporal.api.workflow.v1.WorkflowExecutionInfo;
import io.temporal.api.workflowservice.v1.DescribeWorkflowExecutionResponse;
import io.temporal.api.workflowservice.v1.WorkflowServiceGrpc;
import io.temporal.client.WorkflowClient;
import io.temporal.client.WorkflowClientOptions;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

public class TemporalClientTest {

  private static final String NAMESPACE = "namespace";

  private WorkflowClient workflowClient;
  private TemporalClient temporalClient;
  private WorkflowServiceStubs workflowServiceStubs;
  private WorkflowServiceGrpc.WorkflowServiceBlockingStub workflowServiceBlockingStub;

  @BeforeEach
  void setup() {
    workflowClient = mock(WorkflowClient.class);
    when(workflowClient.getOptions()).thenReturn(WorkflowClientOptions.newBuilder().setNamespace(NAMESPACE).build());

    workflowServiceStubs = mock(WorkflowServiceStubs.class);
    workflowServiceBlockingStub = mock(WorkflowServiceGrpc.WorkflowServiceBlockingStub.class);
    when(workflowServiceStubs.blockingStub()).thenReturn(workflowServiceBlockingStub);
  }

  @Nested
  class RestartPerStatus {

    private ConnectionManagerUtils mConnectionManagerUtils;

    @BeforeEach
    public void init() {
      mConnectionManagerUtils = mock(ConnectionManagerUtils.class);

      temporalClient = spy(
          new TemporalClient(workflowClient, workflowServiceStubs, mConnectionManagerUtils));
    }

    @Test
    void testRestartFailed() {
      final ConnectionManagerWorkflow mConnectionManagerWorkflow = mock(ConnectionManagerWorkflow.class);

      when(workflowClient.newWorkflowStub(any(), anyString())).thenReturn(mConnectionManagerWorkflow);
      final UUID connectionId = UUID.fromString("ebbfdc4c-295b-48a0-844f-88551dfad3db");
      final Set<UUID> workflowIds = Set.of(connectionId);

      doReturn(workflowIds)
          .when(temporalClient).fetchClosedWorkflowsByStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_FAILED);
      doReturn(workflowIds)
          .when(temporalClient).filterOutRunningWorkspaceId(workflowIds);
      mockWorkflowStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_FAILED);
      temporalClient.restartClosedWorkflowByStatus(WorkflowExecutionStatus.WORKFLOW_EXECUTION_STATUS_FAILED);
      verify(mConnectionManagerUtils).safeTerminateWorkflow(eq(workflowClient), eq(connectionId),
          anyString());
      verify(mConnectionManagerUtils).startConnectionManagerNoSignal(eq(workflowClient), eq(connectionId));
    }

  }

  private void mockWorkflowStatus(final WorkflowExecutionStatus status) {
    when(workflowServiceBlockingStub.describeWorkflowExecution(any())).thenReturn(
        DescribeWorkflowExecutionResponse.newBuilder().setWorkflowExecutionInfo(
            WorkflowExecutionInfo.newBuilder().setStatus(status).buildPartial()).build());
  }

}
