/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import io.airbyte.cdk.integrations.destination.StandardNameTransformer;

public class PostgresSQLNameTransformer extends StandardNameTransformer {

  // I _think_ overriding these two methods is sufficient to apply the truncation logic everywhere
  // but this interface + our superclass are weirdly complicated, so plausibly something is missing
  @Override
  public String getIdentifier(final String name) {
    return truncate(super.getIdentifier(name));
  }

  public String convertStreamName(String input) {
    return truncate(super.convertStreamName(input));
  }

  @Override
  public String applyDefaultCase(final String input) {
    return input.toLowerCase();
  }

  @Override
  // see https://github.com/airbytehq/airbyte/issues/35333
  // We cannot delete these method until connectors don't need old v1 raw table references for
  // migration
  @Deprecated
  // Overriding a deprecated method is, itself, a warning
  @SuppressWarnings("deprecation")
  public String getRawTableName(final String streamName) {
    return convertStreamName("_airbyte_raw_" + streamName.toLowerCase());
  }

  /**
   * Postgres silently truncates identifiers to 63 characters. Utility method to do that truncation
   * explicitly, so that we can detect e.g. name collisions.
   */
  private String truncate(String str) {
    return str.substring(0, Math.min(str.length(), 63));
  }

}
