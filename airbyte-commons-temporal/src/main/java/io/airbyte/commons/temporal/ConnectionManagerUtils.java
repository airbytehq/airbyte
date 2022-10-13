/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal;

import io.airbyte.commons.temporal.scheduling.ConnectionManagerWorkflow;
import io.airbyte.commons.temporal.scheduling.ConnectionUpdaterInput;
import io.temporal.client.WorkflowClient;
import jakarta.inject.Singleton;
import java.util.UUID;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@NoArgsConstructor
@Singleton
@Slf4j
public class ConnectionManagerUtils {

  void safeTerminateWorkflow(final WorkflowClient client, final String workflowId, final String reason) {
    log.info("Attempting to terminate existing workflow for workflowId {}.", workflowId);
    try {
      client.newUntypedWorkflowStub(workflowId).terminate(reason);
    } catch (final Exception e) {
      log.warn(
          "Could not terminate temporal workflow due to the following error; "
              + "this may be because there is currently no running workflow for this connection.",
          e);
    }
  }

  public void safeTerminateWorkflow(final WorkflowClient client, final UUID connectionId, final String reason) {
    safeTerminateWorkflow(client, getConnectionManagerName(connectionId), reason);
  }

  public String getConnectionManagerName(final UUID connectionId) {
    return "connection_manager_" + connectionId;
  }

  public ConnectionManagerWorkflow startConnectionManagerNoSignal(final WorkflowClient client, final UUID connectionId) {
    final ConnectionManagerWorkflow connectionManagerWorkflow = newConnectionManagerWorkflowStub(client, connectionId);
    final ConnectionUpdaterInput input = TemporalWorkflowUtils.buildStartWorkflowInput(connectionId);
    WorkflowClient.start(connectionManagerWorkflow::run, input);

    return connectionManagerWorkflow;
  }

  public ConnectionManagerWorkflow newConnectionManagerWorkflowStub(final WorkflowClient client, final UUID connectionId) {
    return client.newWorkflowStub(ConnectionManagerWorkflow.class,
        TemporalWorkflowUtils.buildWorkflowOptions(TemporalJobType.CONNECTION_UPDATER, getConnectionManagerName(connectionId)));
  }

}
