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
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.dataline.config.JobOutput;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardSyncOutput;
import io.dataline.config.State;
import io.dataline.workers.InvalidCatalogException;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.SyncWorker;
import java.nio.file.Path;
import java.util.UUID;
import org.junit.jupiter.api.Test;

public class JobOutputSyncWorkerTest {

  @Test
  public void test() throws InvalidCredentialsException, InvalidCatalogException {
    StandardSyncInput input = mock(StandardSyncInput.class);
    Path jobRoot = Path.of("fakeroot");
    SyncWorker syncWorker = mock(SyncWorker.class);

    StandardSyncOutput output = new StandardSyncOutput().withState(new State().withConnectionId(UUID.randomUUID()));

    when(syncWorker.run(input, jobRoot)).thenReturn(new OutputAndStatus<>(JobStatus.SUCCESSFUL, output));
    OutputAndStatus<JobOutput> run = new JobOutputSyncWorker(syncWorker).run(input, jobRoot);

    JobOutput expected = new JobOutput().withOutputType(JobOutput.OutputType.SYNC).withSync(output);
    assertEquals(JobStatus.SUCCESSFUL, run.getStatus());
    assertTrue(run.getOutput().isPresent());
    assertEquals(expected, run.getOutput().get());
  }

}
