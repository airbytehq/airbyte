package io.airbyte.commons.temporal;

import com.google.inject.Inject;
import io.temporal.api.common.v1.WorkflowType;
import io.temporal.api.enums.v1.WorkflowExecutionStatus;
import io.temporal.api.workflowservice.v1.ListClosedWorkflowExecutionsRequest;
import io.temporal.api.workflowservice.v1.ListClosedWorkflowExecutionsResponse;
import io.temporal.api.workflowservice.v1.ListOpenWorkflowExecutionsRequest;
import io.temporal.api.workflowservice.v1.ListOpenWorkflowExecutionsResponse;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

public class TemporalClient {
  @Inject
  private WorkflowClient client;
  @Inject
  private WorkflowServiceStubs service;
  @Inject
  private ConnectionManagerUtils connectionManagerUtils;

  private final Set<String> workflowNames = new HashSet<>();

  public void restartClosedWorkflowByStatus(final WorkflowExecutionStatus executionStatus) {
    final Set<UUID> workflowExecutionInfos = fetchClosedWorkflowsByStatus(executionStatus);

    final Set<UUID> nonRunningWorkflow = filterOutRunningWorkspaceId(workflowExecutionInfos);

    nonRunningWorkflow.forEach(connectionId -> {
      connectionManagerUtils.safeTerminateWorkflow(client, connectionId, "Terminating workflow in "
          + "unreachable state before starting a new workflow for this connection");
      connectionManagerUtils.startConnectionManagerNoSignal(client, connectionId);
    });
  }

  Set<UUID> fetchClosedWorkflowsByStatus(final WorkflowExecutionStatus executionStatus) {
    ByteString token;
    ListClosedWorkflowExecutionsRequest workflowExecutionsRequest =
        ListClosedWorkflowExecutionsRequest.newBuilder()
            .setNamespace(client.getOptions().getNamespace())
            .build();

    final Set<UUID> workflowExecutionInfos = new HashSet<>();
    do {
      final ListClosedWorkflowExecutionsResponse listOpenWorkflowExecutionsRequest =
          service.blockingStub().listClosedWorkflowExecutions(workflowExecutionsRequest);
      final WorkflowType connectionManagerWorkflowType = WorkflowType.newBuilder().setName(ConnectionManagerWorkflow.class.getSimpleName()).build();
      workflowExecutionInfos.addAll(listOpenWorkflowExecutionsRequest.getExecutionsList().stream()
          .filter(workflowExecutionInfo -> workflowExecutionInfo.getType() == connectionManagerWorkflowType ||
              workflowExecutionInfo.getStatus() == executionStatus)
          .flatMap((workflowExecutionInfo -> extractConnectionIdFromWorkflowId(workflowExecutionInfo.getExecution().getWorkflowId()).stream()))
          .collect(Collectors.toSet()));
      token = listOpenWorkflowExecutionsRequest.getNextPageToken();

      workflowExecutionsRequest =
          ListClosedWorkflowExecutionsRequest.newBuilder()
              .setNamespace(client.getOptions().getNamespace())
              .setNextPageToken(token)
              .build();

    } while (token != null && token.size() > 0);

    return workflowExecutionInfos;
  }

  @VisibleForTesting
  Set<UUID> filterOutRunningWorkspaceId(final Set<UUID> workflowIds) {
    refreshRunningWorkflow();

    final Set<UUID> runningWorkflowByUUID =
        workflowNames.stream().flatMap(name -> extractConnectionIdFromWorkflowId(name).stream()).collect(Collectors.toSet());

    return workflowIds.stream().filter(workflowId -> !runningWorkflowByUUID.contains(workflowId)).collect(Collectors.toSet());
  }

  @VisibleForTesting
  void refreshRunningWorkflow() {
    workflowNames.clear();
    ByteString token;
    ListOpenWorkflowExecutionsRequest openWorkflowExecutionsRequest =
        ListOpenWorkflowExecutionsRequest.newBuilder()
            .setNamespace(client.getOptions().getNamespace())
            .build();
    do {
      final ListOpenWorkflowExecutionsResponse listOpenWorkflowExecutionsRequest =
          service.blockingStub().listOpenWorkflowExecutions(openWorkflowExecutionsRequest);
      final Set<String> workflowExecutionInfos = listOpenWorkflowExecutionsRequest.getExecutionsList().stream()
          .map((workflowExecutionInfo -> workflowExecutionInfo.getExecution().getWorkflowId()))
          .collect(Collectors.toSet());
      workflowNames.addAll(workflowExecutionInfos);
      token = listOpenWorkflowExecutionsRequest.getNextPageToken();

      openWorkflowExecutionsRequest =
          ListOpenWorkflowExecutionsRequest.newBuilder()
              .setNamespace(client.getOptions().getNamespace())
              .setNextPageToken(token)
              .build();

    } while (token != null && token.size() > 0);
  }
}
