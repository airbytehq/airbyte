/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.CONNECTION_ID_KEY;

import datadog.trace.api.Trace;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.commons.temporal.exception.RetryableException;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.helper.ConnectionHelper;
import io.micronaut.context.annotation.Requires;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.Map;

@Singleton
@Requires(env = WorkerMode.CONTROL_PLANE)
public class ConnectionDeletionActivityImpl implements ConnectionDeletionActivity {

  private final ConnectionHelper connectionHelper;

  public ConnectionDeletionActivityImpl(final ConnectionHelper connectionHelper) {
    this.connectionHelper = connectionHelper;
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public void deleteConnection(final ConnectionDeletionInput input) {
    try {
      ApmTraceUtils.addTagsToTrace(Map.of(CONNECTION_ID_KEY, input.getConnectionId()));
      connectionHelper.deleteConnection(input.getConnectionId());
    } catch (final JsonValidationException | ConfigNotFoundException | IOException e) {
      throw new RetryableException(e);
    }
  }

}
