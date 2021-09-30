/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import java.util.UUID;

@VisibleForTesting
public class OracleNameTransformer extends ExtendedNameTransformer {

  @Override
  protected String applyDefaultCase(String input) {
    return input.toUpperCase();
  }

  @Override
  public String getRawTableName(String streamName) {
    return convertStreamName("airbyte_raw_" + streamName);
  }

  @Override
  public String getTmpTableName(String streamName) {
    return convertStreamName("airbyte_tmp_" + streamName + "_" + UUID.randomUUID().toString().replace("-", ""));
  }

  private String maxStringLength(String value, Integer length) {
    if (value.length() <= length) {
      return value;
    }
    return value.substring(0, length);
  }

  @Override
  public String convertStreamName(String input) {
    String result = super.convertStreamName(input);
    if (!result.isEmpty() && result.charAt(0) == '_') {
      result = result.substring(1);
    }
    // prior to Oracle version 12.2, identifiers are not allowed to exceed 30 characters in length.
    // However, from version 12.2 they can be up to 128 bytes long. (Note: bytes, not characters).
    return maxStringLength(result, 30);
  }

}
