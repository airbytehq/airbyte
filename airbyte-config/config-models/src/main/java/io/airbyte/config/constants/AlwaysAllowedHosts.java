/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.constants;

import java.util.ArrayList;
import java.util.List;

public class AlwaysAllowedHosts {

  private final List<String> hosts = new ArrayList<>();

  public AlwaysAllowedHosts() {
    // DataDog. See https://docs.datadoghq.com/agent/proxy/?tab=linux and change the location tabs
    hosts.add("*.datadoghq.com");
    hosts.add("*.datadoghq.eu");

    // Sentry. See https://docs.sentry.io/api/ for more information
    hosts.add("*.sentry.io");
  }

  public List<String> getHosts() {
    return hosts;
  }

}
