/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.util;

public class FlatteningTypeHelper {

  private FlatteningTypeHelper() {}

  /**
   * Sample expected input: { "flattening": "No flattening" }
   */
  // public static FlatteningType parseFlatteningType(final JsonNode flatteningConfig) {
  // if (flatteningConfig == null || flatteningConfig.isNull()) {
  // return DEFAULT_FLATTENING_TYPE;
  // }
  // final String flatteningType = flatteningConfig.get(FLATTENING_ARG_NAME).asText();
  // if (flatteningType.equals(FlatteningType.ROOT_LEVEL.name())) {
  // return FlatteningType.ROOT_LEVEL;
  // } else {
  // return FlatteningType.NO;
  // }
  // }

  // @JsonCreator
  // public static FlatteningType fromValue(final String value) {
  // for (final FlatteningType f : FlatteningType.values()) {
  // if (f.getValue().equalsIgnoreCase(value)) {
  // return f;
  // }
  // }
  // throw new IllegalArgumentException("Unexpected value: " + value);
  // }

}
