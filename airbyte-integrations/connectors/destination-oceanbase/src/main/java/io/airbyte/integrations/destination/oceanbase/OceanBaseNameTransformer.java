/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oceanbase;

import io.airbyte.cdk.integrations.destination.StandardNameTransformer;


public class OceanBaseNameTransformer extends StandardNameTransformer {

  public static final int MAX_OCEANBASE_NAME_LENGTH = 64;
  public static final int TRUNCATE_DBT_RESERVED_SIZE = 12;
  public static final int TRUNCATE_RESERVED_SIZE = 8;
  public static final int TRUNCATION_MAX_NAME_LENGTH = MAX_OCEANBASE_NAME_LENGTH - TRUNCATE_DBT_RESERVED_SIZE - TRUNCATE_RESERVED_SIZE;

  @Override
  public String getIdentifier(final String name) {
    final String identifier = applyDefaultCase(super.getIdentifier(name));
    return truncateName(identifier, TRUNCATION_MAX_NAME_LENGTH);
  }

  @Override
  public String getTmpTableName(final String streamName) {
    final String tmpTableName = applyDefaultCase(super.getTmpTableName(streamName));
    return truncateName(tmpTableName, TRUNCATION_MAX_NAME_LENGTH);
  }

  @Override
  public String getRawTableName(final String streamName) {
    final String rawTableName = applyDefaultCase(super.getRawTableName(streamName));
    return truncateName(rawTableName, TRUNCATION_MAX_NAME_LENGTH);
  }

  static String truncateName(final String name, final int maxLength) {
    if (name.length() <= maxLength) {
      return name;
    }

    final int allowedLength = maxLength - 2;
    final String prefix = name.substring(0, allowedLength / 2);
    final String suffix = name.substring(name.length() - allowedLength / 2);
    return prefix + "__" + suffix;
  }

  @Override
  public String applyDefaultCase(final String input) {
    return input.toLowerCase();
  }

}
