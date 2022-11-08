/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import java.util.Arrays;

/**
 * <ul>
 * <li>An Avro name starts with [A-Za-z_], followed by [A-Za-z0-9_].</li>
 * <li>An Avro namespace is a dot-separated sequence of such names.</li>
 * <li>Reference: https://avro.apache.org/docs/current/spec.html#names</li>
 * </ul>
 */
public class AvroNameTransformer extends ExtendedNameTransformer {

  @Override
  public String applyDefaultCase(final String input) {
    return super.convertStreamName(input).toLowerCase();
  }

  @Override
  public String convertStreamName(final String input) {
    if (input == null) {
      return null;
    } else if (input.isBlank()) {
      return input;
    }

    final String normalizedName = super.convertStreamName(input);
    if (normalizedName.substring(0, 1).matches("[A-Za-z_]")) {
      return normalizedName;
    } else {
      return "_" + normalizedName;
    }
  }

  @Override
  public String getNamespace(final String input) {
    if (input == null) {
      return null;
    }

    final String[] tokens = input.split("\\.");
    return String.join(".", Arrays.stream(tokens).map(this::getIdentifier).toList());
  }

}
