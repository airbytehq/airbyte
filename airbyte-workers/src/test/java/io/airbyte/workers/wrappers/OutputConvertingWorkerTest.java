/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.workers.wrappers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.Worker;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class OutputConvertingWorkerTest {

  @SuppressWarnings("unchecked")
  @Test
  public void testRun() {
    Worker<String, String> worker = Mockito.mock(Worker.class);
    String inputConfig = "input";
    int expectedOutput = 123;
    Path path = Path.of("fakepath");
    when(worker.run(inputConfig, path)).thenReturn(new OutputAndStatus<>(JobStatus.SUCCEEDED, String.valueOf(expectedOutput)));

    OutputAndStatus<Integer> output = new OutputConvertingWorker<String, String, Integer>(worker, Integer::valueOf).run(inputConfig, path);
    assertTrue(output.getOutput().isPresent());
    assertEquals(expectedOutput, output.getOutput().get());
  }

  @SuppressWarnings("unchecked")
  @Test
  public void testCancel() {
    Worker<String, String> worker = Mockito.mock(Worker.class);
    new OutputConvertingWorker<>(worker, Integer::valueOf).cancel();
    verify(worker).cancel();
  }

}
