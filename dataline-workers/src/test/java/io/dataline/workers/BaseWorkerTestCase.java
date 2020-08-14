package io.dataline.workers;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.TestInstance;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public abstract class BaseWorkerTestCase {
  private Path workspaceDirectory;

  @BeforeAll
  public void init() throws IOException {
    workspaceDirectory = Files.createTempDirectory("dataline");
  }

  protected Path getWorkspacePath() {
    return workspaceDirectory;
  }
}
