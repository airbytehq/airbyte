package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.WorkspaceRead;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.config.SlackNotificationConfiguration;
import java.util.UUID;

public class SlackConfigActivityImpl implements SlackConfigActivity {

  private final AirbyteApiClient airbyteApiClient;

  public SlackConfigActivityImpl(AirbyteApiClient airbyteApiClient) { this.airbyteApiClient = airbyteApiClient; }

  public SlackNotificationConfiguration fetchSlackConfiguration(UUID workspaceId) throws ApiException {
    final io.airbyte.api.client.model.generated.WorkspaceIdRequestBody workspaceIdRequestBody = new io.airbyte.api.client.model.generated.WorkspaceIdRequestBody().workspaceId(workspaceId);
    final WorkspaceRead workspaceRead = airbyteApiClient.getWorkspaceApi().getWorkspace(workspaceIdRequestBody);
    workspaceRead.getNotifications();
    return new SlackNotificationConfiguration();
  }
}
