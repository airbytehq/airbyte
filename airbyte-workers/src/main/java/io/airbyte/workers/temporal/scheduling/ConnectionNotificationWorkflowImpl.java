/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling;

import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.commons.temporal.scheduling.ConnectionNotificationWorkflow;
import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.SlackNotificationConfiguration;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.notification.SlackNotificationClient;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.annotations.TemporalActivityStub;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivity;
import io.airbyte.workers.temporal.scheduling.activities.NotifySchemaChangeActivity;
import io.airbyte.workers.temporal.scheduling.activities.SlackConfigActivity;
import io.temporal.workflow.Workflow;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ConnectionNotificationWorkflowImpl implements ConnectionNotificationWorkflow {

  private static final String GET_BREAKING_CHANGE_TAG = "get_breaking_change";
  private static final int GET_BREAKING_CHANGE_VERSION = 1;

  @TemporalActivityStub(activityOptionsBeanName = "shortActivityOptions")
  private NotifySchemaChangeActivity notifySchemaChangeActivity;
  @TemporalActivityStub(activityOptionsBeanName = "shortActivityOptions")
  private SlackConfigActivity slackConfigActivity;
  @TemporalActivityStub(activityOptionsBeanName = "shortActivityOptions")
  private ConfigFetchActivity configFetchActivity;

  @Override
  public boolean sendSchemaChangeNotification(final UUID connectionId)
      throws IOException, InterruptedException, ApiException, ConfigNotFoundException, JsonValidationException {
    final int getBreakingChangeVersion =
        Workflow.getVersion(GET_BREAKING_CHANGE_TAG, Workflow.DEFAULT_VERSION, GET_BREAKING_CHANGE_VERSION);
    if (getBreakingChangeVersion >= GET_BREAKING_CHANGE_VERSION) {
      final Optional<Boolean> breakingChange = configFetchActivity.getBreakingChange(connectionId);
      final Optional<SlackNotificationConfiguration> slackConfig = slackConfigActivity.fetchSlackConfiguration(connectionId);
      if (slackConfig.isPresent() && breakingChange.isPresent()) {
        final Notification notification =
            new Notification().withNotificationType(NotificationType.SLACK).withSendOnFailure(false).withSendOnSuccess(false)
                .withSlackConfiguration(slackConfig.get());
        final SlackNotificationClient notificationClient = new SlackNotificationClient(notification);
        return notifySchemaChangeActivity.notifySchemaChange(notificationClient, connectionId, breakingChange.get());
      } else {
        return false;
      }
    } else {
      return false;
    }
  }

}
