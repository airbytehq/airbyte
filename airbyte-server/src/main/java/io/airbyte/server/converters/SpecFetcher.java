/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import com.google.common.base.Preconditions;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.server.scheduler.SynchronousResponse;

public class SpecFetcher {

  public static ConnectorSpecification getSpecFromJob(final SynchronousResponse<ConnectorSpecification> response) {
    Preconditions.checkState(response.isSuccess(), "Get Spec job failed.");
    Preconditions.checkNotNull(response.getOutput(), "Get Spec job return null spec");

    return response.getOutput();
  }

}
