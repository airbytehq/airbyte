/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Deprecated
public enum DeprecatedConfigsDatabaseTables {

  AIRBYTE_CONFIGS;

  public String getTableName() {
    return name().toLowerCase();
  }

  /**
   * @return table names in lower case
   */
  public static Set<String> getTableNames() {
    return Stream.of(DeprecatedConfigsDatabaseTables.values()).map(DeprecatedConfigsDatabaseTables::getTableName).collect(Collectors.toSet());
  }

}
