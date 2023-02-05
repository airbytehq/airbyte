/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.constants;

import java.util.List;

public class AlwaysAllowedHosts {

  private final List<String> hosts = List.of(
      // DataDog. See https://docs.datadoghq.com/agent/proxy/?tab=linux and change the location tabs
      "*.datadoghq.com",
      "*.datadoghq.eu",

      // Sentry. See https://docs.sentry.io/api/ for more information
      "*.sentry.io");

  public List<String> getHosts() {
    return hosts;
  }

}
