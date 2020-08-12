package io.dataline.workers;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

import org.apache.commons.io.FileUtils;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;

public abstract class BaseWorkerTestCase {
  private Path workspaceDirectory;

  @BeforeAll
  public void init() {
    createTestWorkspace();
    deleteWorkspaceUponJvmExit();
  }

  protected Path getWorkspacePath() {
    return workspaceDirectory;
  }

  private void createTestWorkspace() {
    try {
      workspaceDirectory = Paths.get("/tmp/tests/dataline-" + UUID.randomUUID().toString());
      FileUtils.forceMkdir(workspaceDirectory.toFile());
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private void deleteWorkspaceUponJvmExit() {
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> {
                  try {
                    FileUtils.deleteDirectory(workspaceDirectory.toFile());
                  } catch (IOException e) {
                    throw new RuntimeException(e);
                  }
                }));
  }
}
