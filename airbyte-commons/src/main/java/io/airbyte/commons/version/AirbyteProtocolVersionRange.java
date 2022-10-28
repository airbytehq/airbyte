/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.version;

public class AirbyteProtocolVersionRange {

  private final Version min;
  private final Version max;
  private final Integer minMajor;
  private final Integer maxMajor;

  public AirbyteProtocolVersionRange(final Version min, final Version max) {
    this.min = min;
    this.minMajor = getMajor(min);
    this.max = max;
    this.maxMajor = getMajor(max);
  }

  public boolean isSupported(final Version v) {
    final Integer major = getMajor(v);
    return minMajor <= major && major <= maxMajor;
  }

  public Version getMax() {
    return max;
  }

  public Version getMin() {
    return min;
  }

  private Integer getMajor(final Version v) {
    return Integer.valueOf(v.getMajorVersion());
  }

}
