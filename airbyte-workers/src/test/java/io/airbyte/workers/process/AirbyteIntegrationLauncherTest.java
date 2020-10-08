package io.airbyte.workers.process;

import com.google.common.collect.Lists;
import io.airbyte.workers.WorkerException;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class AirbyteIntegrationLauncherTest {

  private static final Path JOB_ROOT = Path.of("abc");
  public static final String FAKE_IMAGE = "fake_image";

  private ProcessBuilderFactory pbf;
  private AirbyteIntegrationLauncher launcher;

  @BeforeEach
  void setUp() {
    pbf = Mockito.mock(ProcessBuilderFactory.class);
    launcher = new AirbyteIntegrationLauncher(FAKE_IMAGE, pbf);
  }

  @Test
  void spec() throws WorkerException {
    launcher.spec(JOB_ROOT);

    Mockito.verify(pbf).create(JOB_ROOT, FAKE_IMAGE, "spec");
  }

  @Test
  void check() throws WorkerException {
    launcher.check(JOB_ROOT, "config");

    Mockito.verify(pbf).create(JOB_ROOT, FAKE_IMAGE,
        "check",
        "--config", "config");
  }

  @Test
  void discover() throws WorkerException {
    launcher.discover(JOB_ROOT, "config");

    Mockito.verify(pbf).create(JOB_ROOT, FAKE_IMAGE,
        "discover",
        "--config", "config");
  }

  @Test
  void read() throws WorkerException {
    launcher.read(JOB_ROOT, "config", "catalog", "state");

    Mockito.verify(pbf).create(JOB_ROOT, FAKE_IMAGE,
        Lists.newArrayList(
            "read",
            "--config", "config",
            "--catalog", "catalog",
            "--state", "state"));
  }

  @Test
  void write() throws WorkerException {
    launcher.write(JOB_ROOT, "config", "catalog");

    Mockito.verify(pbf).create(JOB_ROOT, FAKE_IMAGE,
        "write",
        "--config", "config",
        "--catalog", "catalog");
  }
}
