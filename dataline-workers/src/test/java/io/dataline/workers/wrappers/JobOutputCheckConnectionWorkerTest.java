package io.dataline.workers.wrappers;

import com.google.common.collect.Lists;
import io.dataline.config.JobOutput;
import io.dataline.config.Schema;
import io.dataline.config.StandardCheckConnectionInput;
import io.dataline.config.StandardCheckConnectionOutput;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.config.Table;
import io.dataline.workers.CheckConnectionWorker;
import io.dataline.workers.DiscoverSchemaWorker;
import io.dataline.workers.InvalidCatalogException;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import org.junit.jupiter.api.Test;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class JobOutputCheckConnectionWorkerTest {
  @Test
  public void test() throws InvalidCredentialsException, InvalidCatalogException {
    StandardCheckConnectionInput input = mock(StandardCheckConnectionInput.class);
    Path jobRoot = Path.of("fakeroot");
    CheckConnectionWorker checkConnectionWorker = mock(CheckConnectionWorker.class);

    StandardCheckConnectionOutput output = new StandardCheckConnectionOutput().withMessage("hello world");

    when(checkConnectionWorker.run(input, jobRoot)).thenReturn(new OutputAndStatus<>(JobStatus.SUCCESSFUL, output));
    OutputAndStatus<JobOutput> run = new JobOutputCheckConnectionWorker(checkConnectionWorker).run(input, jobRoot);

    JobOutput expected = new JobOutput().withOutputType(JobOutput.OutputType.CHECK_CONNECTION).withCheckConnection(output);
    assertEquals(JobStatus.SUCCESSFUL, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(expected, run.getOutput().get());
  }
}
