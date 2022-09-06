/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

public class AirbyteProtocolVersion {

  public static String DEFAULT_AIRBYTE_PROTOCOL_VERSION = "0.2.0";

  public static String getWithDefault(String version) {
    if (version == null || version.isEmpty() || version.isBlank()) {
      return DEFAULT_AIRBYTE_PROTOCOL_VERSION;
    } else {
      return version;
    }
  }

}
