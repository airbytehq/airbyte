/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

public class AirbyteProtocolVersion {

  public static final Version DEFAULT_AIRBYTE_PROTOCOL_VERSION = new Version("0.2.0");
  public static final Version V0 = new Version("0.3.0");
  public static final Version V1 = new Version("1.0.0");

  public static final String AIRBYTE_PROTOCOL_VERSION_MAX_KEY_NAME = "airbyte_protocol_version_max";
  public static final String AIRBYTE_PROTOCOL_VERSION_MIN_KEY_NAME = "airbyte_protocol_version_min";

  public static Version getWithDefault(final String version) {
    if (version == null || version.isEmpty() || version.isBlank()) {
      return DEFAULT_AIRBYTE_PROTOCOL_VERSION;
    } else {
      return new Version(version);
    }
  }
}
