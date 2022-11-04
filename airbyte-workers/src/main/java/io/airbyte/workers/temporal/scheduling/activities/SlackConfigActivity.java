package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.SlackNotificationConfiguration;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface SlackConfigActivity {

  @ActivityMethod
  public SlackNotificationConfiguration fetchSlackConfiguration()
}
