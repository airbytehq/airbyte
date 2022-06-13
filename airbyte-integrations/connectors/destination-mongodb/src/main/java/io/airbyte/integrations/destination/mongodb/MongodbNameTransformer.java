/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.destination.ExtendedNameTransformer;

@VisibleForTesting
public class MongodbNameTransformer extends ExtendedNameTransformer {

  @Override
  public String applyDefaultCase(final String input) {
    return input.toLowerCase();
  }

  @Override
  public String convertStreamName(final String input) {
    String result = super.convertStreamName(input);
    if (!result.isEmpty() && result.charAt(0) == '_') {
      result = result.substring(1);
    }
    return maxStringLength(result, 64);
  }

  /* Helpers */

  private String maxStringLength(final String value, final Integer length) {
    if (value.length() <= length) {
      return value;
    }
    return value.substring(0, length);
  }

}
