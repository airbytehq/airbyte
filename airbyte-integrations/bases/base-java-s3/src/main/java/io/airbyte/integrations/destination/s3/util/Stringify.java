/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import com.fasterxml.jackson.annotation.JsonCreator;

public enum Stringify {

  NO("Default"),
  STRINGIFY("Stringify");

  private final String value;

  Stringify(final String value) {
    this.value = value;
  }

  public String getValue() {
    return value;
  }

  @JsonCreator
  public static Stringify fromValue(final String value) {
    for (final Stringify s : Stringify.values()) {
      if (s.getValue().equalsIgnoreCase(value)) {
        return s;
      }
    }
    throw new IllegalArgumentException("Unexpected value: " + value);
  }

}
