package io.dataline.db;

import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;
import java.io.IOException;
import java.util.UUID;

public class PostgreSQLContainerHelper {

  public static void runSqlScript(MountableFile file, PostgreSQLContainer db) {
    try {
      String scriptPath = "/etc/" + UUID.randomUUID().toString() + ".sql";
      db.copyFileToContainer(file, scriptPath);
      db.execInContainer(
          "psql", "-d", db.getDatabaseName(), "-U", db.getUsername(), "-a", "-f", scriptPath);

    } catch (InterruptedException | IOException e) {
      throw new RuntimeException(e);
    }
  }
}
