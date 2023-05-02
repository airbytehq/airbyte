/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import io.airbyte.integrations.destination.StandardNameTransformer;

public class RedshiftSQLNameTransformer extends StandardNameTransformer {

  @Override
  public String convertStreamName(final String input) {
    return super.convertStreamName(input).toLowerCase();
  }

}
