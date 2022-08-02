/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.constants;

import java.util.List;

public class DockerImageName {

  public static final List<String> MYSQL_DOCKER_IMAGES = List.of("airbyte/source-mysql", "airbyte/source-mysql-strict-encrypt");
  public static final List<String> MSSQL_DOCKER_IMAGES = List.of("airbyte/source-mssql", "airbyte/source-mssql-strict-encrypt");
  public static final List<String> MYSQL_REPLICATION_ERRORS = List.of("$.replication_method: string found, object expected",
      "$.replication_method: does not have a value in the enumeration [STANDARD, CDC]");

}
