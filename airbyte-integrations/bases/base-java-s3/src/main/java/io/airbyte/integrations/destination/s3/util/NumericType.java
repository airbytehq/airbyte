/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

import com.fasterxml.jackson.annotation.JsonCreator;

public enum NumericType {

  DOUBLE("Double"),
  DECIMAL("Decimal");

  private final String value;

  NumericType(final String value) {
    this.value = value;
  }

  public String getValue() {
    return value;
  }

  @JsonCreator
  public static NumericType fromValue(final String value) {
    for (final NumericType s : NumericType.values()) {
      if (s.getValue().equalsIgnoreCase(value)) {
        return s;
      }
    }
    throw new IllegalArgumentException("Unexpected value: " + value);
  }

}
