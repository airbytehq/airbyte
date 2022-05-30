/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class SnowflakeSQLNameTransformer extends ExtendedNameTransformer {

  @Override
  public String applyDefaultCase(final String input) {
    return input.toUpperCase();
  }

  /**
   * The first character can only be alphanumeric or an underscore.
   */
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
