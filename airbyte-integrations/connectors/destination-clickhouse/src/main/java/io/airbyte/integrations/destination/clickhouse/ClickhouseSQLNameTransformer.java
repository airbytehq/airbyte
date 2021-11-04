/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class ClickhouseSQLNameTransformer extends ExtendedNameTransformer {

  @Override
  protected String applyDefaultCase(final String input) {
    return input.toLowerCase();
  }

}
