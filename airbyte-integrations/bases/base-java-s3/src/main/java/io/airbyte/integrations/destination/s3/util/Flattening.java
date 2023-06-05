/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import com.fasterxml.jackson.annotation.JsonCreator;

public enum Flattening {

  NO("No flattening"),
  ROOT_LEVEL("Root level flattening");

  private final String value;

  Flattening(final String value) {
    this.value = value;
  }

  public String getValue() {
    return value;
  }

  @JsonCreator
  public static Flattening fromValue(final String value) {
    for (final Flattening f : Flattening.values()) {
      if (f.getValue().equalsIgnoreCase(value)) {
        return f;
      }
    }
    throw new IllegalArgumentException("Unexpected value: " + value);
  }

}
