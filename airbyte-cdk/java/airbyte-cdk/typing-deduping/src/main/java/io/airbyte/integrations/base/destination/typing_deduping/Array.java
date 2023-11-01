/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public record Array(AirbyteType items) implements AirbyteType {

  public static final String ARRAY = "ARRAY";

  @Override
  public String getTypeName() {
    return ARRAY;
  }

}
