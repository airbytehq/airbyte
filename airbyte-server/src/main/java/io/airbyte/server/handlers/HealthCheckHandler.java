/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.HealthCheckRead;

public class HealthCheckHandler {

  public HealthCheckRead health() {
    return new HealthCheckRead().available(true);
  }

}
