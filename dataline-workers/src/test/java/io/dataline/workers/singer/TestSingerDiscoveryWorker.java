package io.dataline.workers.singer;

import io.dataline.workers.DiscoveryOutput;
import io.dataline.workers.OutputAndStatus;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static io.dataline.workers.JobStatus.SUCCESSFUL;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class TestSingerDiscoveryWorker {
  // TODO pending installing singer binaries into the workspace
  @Test
  public void testDiscoveryWorker() {
    
    SingerDiscoveryWorker worker =
        new SingerDiscoveryWorker(
            UUID.randomUUID().toString(),
            "",
            SingerTap.POSTGRES,
            "/workspace/workers",
            "/lib/singer/");

    OutputAndStatus<DiscoveryOutput> run = worker.run();
    assertEquals(SUCCESSFUL, run.status);

    String expectedCatalog = "";
    assertTrue(run.output.isPresent());
    assertEquals(expectedCatalog, run.output.get().catalog);
  }
}
