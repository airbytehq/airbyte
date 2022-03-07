/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mariadb_columnstore;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class MariadbColumnstoreNameTransformer extends ExtendedNameTransformer {

  @Override
  public String getIdentifier(final String name) {
    return applyDefaultCase(super.getIdentifier(name));
  }

  @Override
  protected String applyDefaultCase(final String input) {
    return input.toLowerCase();
  }

}
