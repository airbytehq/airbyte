package io.airbyte.commons.temporal;

import io.temporal.client.WorkflowClient;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

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
}
