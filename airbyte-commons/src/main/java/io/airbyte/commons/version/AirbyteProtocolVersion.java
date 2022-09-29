/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

public class AirbyteProtocolVersion {

  public final static Version DEFAULT_AIRBYTE_PROTOCOL_VERSION = new Version("0.2.0");

  public static Version getWithDefault(final String version) {
    if (version == null || version.isEmpty() || version.isBlank()) {
      return DEFAULT_AIRBYTE_PROTOCOL_VERSION;
    } else {
      return new Version(version);
    }
  }

}
