package io.dataline.workers.wrappers;

import io.dataline.workers.InvalidCatalogException;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.Worker;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.Mockito;

import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.when;

public class OutputConvertingWorkerTest {
  @Test
  public void test() throws InvalidCredentialsException, InvalidCatalogException {
    Worker<String, String> worker = Mockito.mock(Worker.class);
    String inputConfig = "input";
    int expectedOutput = 123;
    when(worker.run(inputConfig, Mockito.any())).thenReturn(new OutputAndStatus<>(JobStatus.SUCCESSFUL, String.valueOf(expectedOutput)));

    OutputAndStatus<Integer> output = new OutputConvertingWorker<String, String, Integer>(worker) {

      @Override protected Integer convert(String output) {
        return Integer.valueOf(output);
      }
    }.run(inputConfig, Path.of("fakepath"));
    assertTrue(output.getOutput().isPresent());
    assertEquals(expectedOutput, output.getOutput().get());
  }
}
