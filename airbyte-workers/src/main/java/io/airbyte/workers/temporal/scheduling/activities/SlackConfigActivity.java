package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.config.SlackNotificationConfiguration;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.util.UUID;

@ActivityInterface
public interface SlackConfigActivity {

  @ActivityMethod
  public SlackNotificationConfiguration fetchSlackConfiguration(UUID connectionId) throws ApiException;
}
