/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.util;

import java.util.Objects;
import org.testcontainers.containers.GenericContainer;

public class HostPortResolver {

  public static String resolveHost(GenericContainer container) {
    return System.getProperty("os.name").toLowerCase().startsWith("mac") ? Objects.requireNonNull(container.getContainerInfo()
        .getNetworkSettings()
        .getNetworks()
        .entrySet().stream()
        .findFirst()
        .get().getValue().getIpAddress())
        : container.getHost();
  }

  public static int resolvePort(GenericContainer container) {
    return System.getProperty("os.name").toLowerCase().startsWith("mac") ? (Integer) container.getExposedPorts().get(0)
        : container.getFirstMappedPort();
  }

}
