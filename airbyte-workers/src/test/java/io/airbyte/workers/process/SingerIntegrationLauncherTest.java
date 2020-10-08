package io.airbyte.workers.process;

import io.airbyte.workers.WorkerException;
import java.nio.file.Path;
import org.apache.commons.lang3.NotImplementedException;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class SingerIntegrationLauncherTest {

  private static final Path JOB_ROOT = Path.of("abc");
  public static final String FAKE_IMAGE = "fake_image";

  private ProcessBuilderFactory pbf;
  private SingerIntegrationLauncher launcher;

  @BeforeEach
  void setUp() {
    pbf = Mockito.mock(ProcessBuilderFactory.class);
    launcher = new SingerIntegrationLauncher(FAKE_IMAGE, pbf);
  }

  @Test
  void spec() {
    Assertions.assertThrows(
        NotImplementedException.class,
        () -> launcher.spec(JOB_ROOT)
    );
  }

  @Test
  void check() {
    Assertions.assertThrows(
        NotImplementedException.class,
        () -> launcher.check(JOB_ROOT, "abc")
    );
  }

  @Test
  void discover() throws WorkerException {
    launcher.discover(JOB_ROOT, "abc");

    Mockito.verify(pbf).create(JOB_ROOT, FAKE_IMAGE,
        "--config", "abc",
        "--discover");
  }

  @Test
  void read() throws WorkerException {
    launcher.read(JOB_ROOT, "config", "catalog", "state");

    Mockito.verify(pbf).create(JOB_ROOT, FAKE_IMAGE,
        "--config", "config",
        "--properties", "catalog",
        "--state", "state");
  }

  @Test
  void write() throws WorkerException {
    launcher.write(JOB_ROOT, "config", "catalog");

    Mockito.verify(pbf).create(JOB_ROOT, FAKE_IMAGE, "--config", "config");
  }
}
