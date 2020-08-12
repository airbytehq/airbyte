package io.dataline.workers;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;
import org.apache.commons.io.*;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;

public abstract class BaseWorkerTestCase {
  private Path workspaceDirectory;

  @BeforeAll
  public void init() {

    Runtime.getRuntime().addShutdownHook(new Thread(() -> {}));
  }

  @AfterAll
  public void teardown() {}

  protected Path getWorkspacePath() {
    return workspaceDirectory;
  }

  private void createTestWorkspace() {
    try {

      workspaceDirectory =
          Files.createDirectories(Paths.get("/tmp/tests/dataline-" + UUID.randomUUID().toString()));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private void deleteTestWorkspace() {}
}
