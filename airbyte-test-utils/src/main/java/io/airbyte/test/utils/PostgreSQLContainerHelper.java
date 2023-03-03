/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.utils;

import java.io.IOException;
import java.util.UUID;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class PostgreSQLContainerHelper {

  public static void runSqlScript(final MountableFile file, final PostgreSQLContainer db) {
    try {
      final String scriptPath = "/etc/" + UUID.randomUUID() + ".sql";
      db.copyFileToContainer(file, scriptPath);
      db.execInContainer(
          "psql", "-d", db.getDatabaseName(), "-U", db.getUsername(), "-a", "-f", scriptPath);

    } catch (final InterruptedException | IOException e) {
      throw new RuntimeException(e);
    }
  }

}
