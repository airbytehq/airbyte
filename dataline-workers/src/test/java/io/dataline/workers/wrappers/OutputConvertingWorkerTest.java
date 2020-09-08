/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.workers.wrappers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.when;

import io.dataline.workers.InvalidCatalogException;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.Worker;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class OutputConvertingWorkerTest {

  @Test
  public void test() throws InvalidCredentialsException, InvalidCatalogException {
    Worker<String, String> worker = Mockito.mock(Worker.class);
    String inputConfig = "input";
    int expectedOutput = 123;
    Path path = Path.of("fakepath");
    when(worker.run(inputConfig, path)).thenReturn(new OutputAndStatus<>(JobStatus.SUCCESSFUL, String.valueOf(expectedOutput)));

    OutputAndStatus<Integer> output = new OutputConvertingWorker<String, String, Integer>(worker) {

      @Override
      protected Integer convert(String output) {
        return Integer.valueOf(output);
      }

    }.run(inputConfig, path);
    assertTrue(output.getOutput().isPresent());
    assertEquals(expectedOutput, output.getOutput().get());
  }

}
