/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class AvroNameTransformer extends ExtendedNameTransformer {

  @Override
  public String applyDefaultCase(final String input) {
    return super.convertStreamName(input).toLowerCase();
  }

  @Override
  public String convertStreamName(final String input) {
    if (input == null) {
      return null;
    }

    final String normalizedName = super.convertStreamName(input);
    if (normalizedName.substring(0, 1).matches("[A-Za-z_]")) {
      return normalizedName;
    } else {
      return "_" + normalizedName;
    }
  }

}
