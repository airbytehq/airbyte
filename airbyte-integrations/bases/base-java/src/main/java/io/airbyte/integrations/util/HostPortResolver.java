/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.util;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import org.testcontainers.containers.GenericContainer;

public class HostPortResolver {

  public static String resolveHost(GenericContainer container) {
    return getIpAddress(container);
  }

  public static int resolvePort(GenericContainer container) {
    return (Integer) container.getExposedPorts().stream().findFirst().get();
  }

  public static String resolveIpAddress(GenericContainer container) {
    return getIpAddress(container);
  }

  public static String encodeValue(final String value) {
    if (value != null) {
      return URLEncoder.encode(value, StandardCharsets.UTF_8);
    }
    return null;
  }

  private static String getIpAddress(GenericContainer container) {
    return Objects.requireNonNull(container.getContainerInfo()
        .getNetworkSettings()
        .getNetworks()
        .entrySet().stream()
        .findFirst()
        .get().getValue().getIpAddress());
  }

}
