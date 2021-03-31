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

package io.airbyte.workers.temporal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.atLeast;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.Worker;
import io.temporal.internal.common.CheckedExceptionWrapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.function.BiConsumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.stubbing.Answer;

class TemporalAttemptExecutionTest {

  private static final String JOB_ID = "11";
  private static final int ATTEMPT_ID = 21;
  private static final JobRunConfig JOB_RUN_CONFIG = new JobRunConfig().withJobId(JOB_ID).withAttemptId((long) ATTEMPT_ID);

  private Path jobRoot;

  private CheckedSupplier<Worker<String, String>, Exception> execution;
  private BiConsumer<Path, String> mdcSetter;

  private TemporalAttemptExecution<String, String> attemptExecution;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws IOException {
    final Path workspaceRoot = Files.createTempDirectory(Path.of("/tmp"), "temporal_attempt_execution_test");
    jobRoot = workspaceRoot.resolve(JOB_ID).resolve(String.valueOf(ATTEMPT_ID));

    execution = mock(CheckedSupplier.class);
    mdcSetter = mock(BiConsumer.class);
    final CheckedConsumer<Path, IOException> jobRootDirCreator = Files::createDirectories;

    attemptExecution = new TemporalAttemptExecution<>(
        workspaceRoot,
        JOB_RUN_CONFIG, execution,
        () -> "",
        mdcSetter,
        jobRootDirCreator,
        mock(CancellationHandler.class), () -> "workflow_id");
  }

  @SuppressWarnings("unchecked")
  @Test
  void testSuccessfulSupplierRun() throws Exception {
    final String expected = "louis XVI";
    final Worker<String, String> worker = mock(Worker.class);
    when(worker.run(any(), any())).thenReturn(expected);

    when(execution.get()).thenAnswer((Answer<Worker<String, String>>) invocation -> worker);

    final String actual = attemptExecution.get();

    assertEquals(expected, actual);

    verify(execution).get();
    verify(mdcSetter, atLeast(2)).accept(jobRoot, JOB_ID);
  }

  @Test
  void testThrowsCheckedException() throws Exception {
    when(execution.get()).thenThrow(new IOException());

    final CheckedExceptionWrapper actualException = assertThrows(CheckedExceptionWrapper.class, () -> attemptExecution.get());
    assertEquals(IOException.class, CheckedExceptionWrapper.unwrap(actualException).getClass());

    verify(execution).get();
    verify(mdcSetter).accept(jobRoot, JOB_ID);
  }

  @Test
  void testThrowsUnCheckedException() throws Exception {
    when(execution.get()).thenThrow(new IllegalArgumentException());

    assertThrows(IllegalArgumentException.class, () -> attemptExecution.get());

    verify(execution).get();
    verify(mdcSetter).accept(jobRoot, JOB_ID);
  }

}
