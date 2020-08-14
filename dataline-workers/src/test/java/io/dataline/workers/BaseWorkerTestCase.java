package io.dataline.workers;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;
import org.apache.commons.io.FileUtils;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public abstract class BaseWorkerTestCase {
  private Path workspaceDirectory;

  @BeforeAll
  public void init() {
    createTestWorkspace();
    try {
      FileUtils.forceDeleteOnExit(workspaceDirectory.toFile());
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  protected Path getWorkspacePath() {
    return workspaceDirectory;
  }

  private void createTestWorkspace() {
    try {
      workspaceDirectory =
          Paths.get("/tmp/tests/dataline-" + UUID.randomUUID().toString().substring(0, 8));
      FileUtils.forceMkdir(workspaceDirectory.toFile());
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }
}
