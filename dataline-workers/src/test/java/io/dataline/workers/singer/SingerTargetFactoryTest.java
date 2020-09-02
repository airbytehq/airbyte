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

package io.dataline.workers.singer;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.dataline.commons.functional.CloseableConsumer;
import io.dataline.commons.json.Jsons;
import io.dataline.config.SingerMessage;
import io.dataline.config.StandardTargetConfig;
import io.dataline.workers.DefaultSyncWorker;
import io.dataline.workers.TestConfigHelpers;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import io.dataline.workers.protocol.singer.MessageUtils;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SingerTargetFactoryTest {

  private static final String IMAGE_NAME = "spark_streaming:latest";
  private static final String JOB_ROOT_PREFIX = "workspace";
  private static final String TABLE_NAME = "user_preferences";
  private static final String COLUMN_NAME = "favorite_color";

  private Path jobRoot;
  private ProcessBuilderFactory pbf;
  private ProcessBuilder processBuilder;
  private Process process;
  ByteArrayOutputStream outputStream;

  @BeforeEach
  public void setup() throws IOException {
    jobRoot = Files.createTempDirectory(JOB_ROOT_PREFIX);

    pbf = mock(ProcessBuilderFactory.class);
    processBuilder = mock(ProcessBuilder.class);
    process = mock(Process.class);
    outputStream = new ByteArrayOutputStream();
  }

  @Test
  public void test() throws Exception {
    when(pbf.create(jobRoot, IMAGE_NAME, "--config", jobRoot.resolve(SingerTargetFactory.CONFIG_JSON_FILENAME).toString()))
        .thenReturn(processBuilder);
    when(processBuilder.redirectError(jobRoot.resolve(DefaultSyncWorker.TARGET_ERR_LOG).toFile())).thenReturn(processBuilder);
    when(processBuilder.start()).thenReturn(process);
    when(process.getOutputStream()).thenReturn(outputStream);

    final StandardTargetConfig targetConfig =
        WorkerUtils.syncToTargetConfig(TestConfigHelpers.createSyncConfig().getValue());

    final SingerTargetFactory targetFactory = new SingerTargetFactory(IMAGE_NAME, pbf);
    final CloseableConsumer<SingerMessage> closeableConsumer = targetFactory.create(targetConfig, jobRoot);

    verify(pbf).create(jobRoot, IMAGE_NAME, "--config", jobRoot.resolve(SingerTargetFactory.CONFIG_JSON_FILENAME).toString());
    verify(processBuilder).redirectError(jobRoot.resolve(DefaultSyncWorker.TARGET_ERR_LOG).toFile());
    verify(processBuilder).start();
    verify(process).getOutputStream();

    SingerMessage recordMessage = MessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "blue");
    closeableConsumer.accept(recordMessage);
    closeableConsumer.close();

    String actualOutput = new String(outputStream.toByteArray());
    assertEquals(Jsons.serialize(recordMessage) + "\n", actualOutput);
  }

}
