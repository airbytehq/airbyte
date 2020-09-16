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

package io.dataline.workers.protocols.singer;

import static org.junit.Assert.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardTargetConfig;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.TestConfigHelpers;
import io.dataline.workers.WorkerConstants;
import io.dataline.workers.WorkerException;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultSingerTargetTest {

  private static final String IMAGE_NAME = "spark_streaming:latest";
  private static final String JOB_ROOT_PREFIX = "workspace";
  private static final String TABLE_NAME = "user_preferences";
  private static final String COLUMN_NAME = "favorite_color";

  private static final StandardTargetConfig TARGET_CONFIG = WorkerUtils.syncToTargetConfig(TestConfigHelpers.createSyncConfig().getValue());

  private Path jobRoot;
  private ProcessBuilderFactory pbf;
  private Process process;
  private ByteArrayOutputStream outputStream;

  @BeforeEach
  public void setup() throws IOException {
    jobRoot = Files.createTempDirectory(JOB_ROOT_PREFIX);

    process = mock(Process.class);
    outputStream = spy(new ByteArrayOutputStream());
    when(process.getOutputStream()).thenReturn(outputStream);

    pbf = mock(ProcessBuilderFactory.class, RETURNS_DEEP_STUBS);
    when(pbf.create(jobRoot, IMAGE_NAME, "--config", WorkerConstants.TARGET_CONFIG_JSON_FILENAME)
        .redirectError(jobRoot.resolve(WorkerConstants.TARGET_ERR_LOG).toFile())
        .start())
            .thenReturn(process);
  }

  @Test
  public void testSuccessfulLifecycle() throws Exception {
    final SingerTarget target = new DefaultSingerTarget(IMAGE_NAME, pbf);
    target.start(TARGET_CONFIG, jobRoot);

    final SingerMessage recordMessage = SingerMessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "blue");
    target.accept(recordMessage);

    verify(outputStream, never()).close();

    target.notifyEndOfStream();

    verify(outputStream).close();

    target.close();

    final String actualOutput = new String(outputStream.toByteArray());
    assertEquals(Jsons.serialize(recordMessage) + "\n", actualOutput);

    verify(process).waitFor(anyLong(), any());
  }

  @Test
  public void testCloseNotifiesLifecycle() throws Exception {
    final SingerTarget target = new DefaultSingerTarget(IMAGE_NAME, pbf);
    target.start(TARGET_CONFIG, jobRoot);

    verify(outputStream, never()).close();

    target.close();
    verify(outputStream).close();
  }

  @Test
  public void testProcessFailLifecycle() throws Exception {
    final SingerTarget target = new DefaultSingerTarget(IMAGE_NAME, pbf);
    target.start(TARGET_CONFIG, jobRoot);

    when(process.exitValue()).thenReturn(1);
    Assertions.assertThrows(WorkerException.class, target::close);
  }

}
