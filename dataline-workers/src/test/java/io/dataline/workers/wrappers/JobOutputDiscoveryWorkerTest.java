package io.dataline.workers.wrappers;

import com.google.common.collect.Lists;
import io.dataline.config.JobOutput;
import io.dataline.config.Schema;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardSyncOutput;
import io.dataline.config.State;
import io.dataline.config.Table;
import io.dataline.workers.DiscoverSchemaWorker;
import io.dataline.workers.InvalidCatalogException;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.SyncWorker;
import org.junit.jupiter.api.Test;
import java.nio.file.Path;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class JobOutputDiscoveryWorkerTest {

  @Test
  public void test() throws InvalidCredentialsException, InvalidCatalogException {
    StandardDiscoverSchemaInput input = mock(StandardDiscoverSchemaInput.class);
    Path jobRoot = Path.of("fakeroot");
    DiscoverSchemaWorker discoverWorker = mock(DiscoverSchemaWorker.class);

    StandardDiscoverSchemaOutput output = new StandardDiscoverSchemaOutput().withSchema(
        new Schema().withTables(Lists.newArrayList(new Table().withName("table")))
    );

    when(discoverWorker.run(input, jobRoot)).thenReturn(new OutputAndStatus<>(JobStatus.SUCCESSFUL, output));
    OutputAndStatus<JobOutput> run = new JobOutputDiscoverSchemaWorker(discoverWorker).run(input, jobRoot);

    JobOutput expected = new JobOutput().withOutputType(JobOutput.OutputType.DISCOVER_SCHEMA).withDiscoverSchema(output);
    assertEquals(JobStatus.SUCCESSFUL, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(expected, run.getOutput().get());
  }
}
