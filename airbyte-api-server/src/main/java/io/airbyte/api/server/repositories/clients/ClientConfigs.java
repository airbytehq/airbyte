/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.server.repositories.clients;

import io.micronaut.context.annotation.ConfigurationProperties;
import io.micronaut.context.annotation.Requires;

@ConfigurationProperties(ClientConfigs.PREFIX)
@Requires(property = ClientConfigs.PREFIX)
public class ClientConfigs {

  public static final String PREFIX = "config-api";
  public static final String API_URL = "http://" + "${airbyte.internal.api.host}";

}
