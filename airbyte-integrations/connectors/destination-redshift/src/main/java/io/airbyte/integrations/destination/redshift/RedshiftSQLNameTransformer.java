/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class RedshiftSQLNameTransformer extends ExtendedNameTransformer {

  @Override
  public String convertStreamName(String input) {
    return super.convertStreamName(input).toLowerCase();
  }

}
