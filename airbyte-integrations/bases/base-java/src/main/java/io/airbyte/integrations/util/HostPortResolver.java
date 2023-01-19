/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.util;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Objects;
import org.testcontainers.containers.GenericContainer;

public class HostPortResolver {

  public static String resolveHost(GenericContainer container) {
    return System.getProperty("os.name").toLowerCase().startsWith("mac")
        ? getIpAddress(container)
        : container.getHost();
  }

  public static int resolvePort(GenericContainer container) {
    return System.getProperty("os.name").toLowerCase().startsWith("mac") ? (Integer) container.getExposedPorts().get(0)
        : container.getFirstMappedPort();
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
