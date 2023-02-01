/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling;

import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.io.IOException;
import java.util.UUID;

@WorkflowInterface
public interface ConnectionNotificationWorkflow {

  @WorkflowMethod
  boolean sendSchemaChangeNotification(UUID connectionId)
      throws IOException, InterruptedException, ApiException, ConfigNotFoundException, JsonValidationException;

}
