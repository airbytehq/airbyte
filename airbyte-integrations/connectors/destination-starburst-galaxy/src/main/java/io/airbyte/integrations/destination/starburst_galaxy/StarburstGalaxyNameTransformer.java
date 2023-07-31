/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static java.util.Locale.ENGLISH;

import io.airbyte.integrations.destination.StandardNameTransformer;

public class StarburstGalaxyNameTransformer
    extends StandardNameTransformer {

  @Override
  public String convertStreamName(final String input) {
    return applyDefaultCase(super.convertStreamName(input));
  }

  @Override
  public String getIdentifier(final String name) {
    return applyDefaultCase(super.getIdentifier(name));
  }

  @Override
  public String getTmpTableName(final String streamName) {
    return applyDefaultCase(super.getTmpTableName(streamName));
  }

  @Override
  public String getRawTableName(final String streamName) {
    return applyDefaultCase(super.getRawTableName(streamName));
  }

  @Override
  public String applyDefaultCase(final String input) {
    return input.toLowerCase(ENGLISH);
  }

}
