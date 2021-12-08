/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public enum ConfigsDatabase2Tables {

  WORKSPACE,
  ACTOR_DEFINITION,
  ACTOR,
  ACTOR_OAUTH_PARAMETER,
  OPERATION,
  CONNECTION,
  CONNECTION_OPERATION,
  STATE;

  public String getTableName() {
    return name().toLowerCase();
  }

  /**
   * @return table names in lower case
   */
  public static Set<String> getTableNames() {
    return Stream.of(ConfigsDatabase2Tables.values()).map(ConfigsDatabase2Tables::getTableName).collect(Collectors.toSet());
  }

}
