/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

public record AirbyteProtocolVersionRange(Version min, Version max) {

  public boolean isSupported(final Version v) {
    final Integer major = getMajor(v);
    return getMajor(min) <= major && major <= getMajor(max);
  }

  private Integer getMajor(final Version v) {
    return Integer.valueOf(v.getMajorVersion());
  }

}
