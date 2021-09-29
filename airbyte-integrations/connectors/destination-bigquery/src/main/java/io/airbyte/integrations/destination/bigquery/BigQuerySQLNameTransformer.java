/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import io.airbyte.integrations.destination.StandardNameTransformer;

public class BigQuerySQLNameTransformer extends StandardNameTransformer {

  @Override
  public String convertStreamName(String input) {
    String result = super.convertStreamName(input);
    if (!result.substring(0, 1).matches("[A-Za-z_]")) {
      // has to start with a letter or _
      result = "_" + result;
    }
    return result;
  }

}
