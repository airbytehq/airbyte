/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mariadb_columnstore;

import io.airbyte.integrations.destination.StandardNameTransformer;

public class MariadbColumnstoreNameTransformer extends StandardNameTransformer {

  @Override
  public String getIdentifier(final String name) {
    return applyDefaultCase(super.getIdentifier(name));
  }

  @Override
  public String applyDefaultCase(final String input) {
    return input.toLowerCase();
  }

}
