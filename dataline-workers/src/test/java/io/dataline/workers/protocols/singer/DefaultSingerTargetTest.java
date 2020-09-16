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
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardTargetConfig;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.TestConfigHelpers;
import io.dataline.workers.WorkerConstants;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultSingerTargetTest {

  private static final String IMAGE_NAME = "spark_streaming:latest";
  private static final String JOB_ROOT_PREFIX = "workspace";
  private static final String TABLE_NAME = "user_preferences";
  private static final String COLUMN_NAME = "favorite_color";

  private Path jobRoot;
  private ProcessBuilderFactory pbf;
  private Process process;
  private ByteArrayOutputStream outputStream;

  @BeforeEach
  public void setup() throws IOException {
    jobRoot = Files.createTempDirectory(JOB_ROOT_PREFIX);

    pbf = mock(ProcessBuilderFactory.class, RETURNS_DEEP_STUBS);
    process = mock(Process.class);
    outputStream = new ByteArrayOutputStream();
  }

  @Test
  public void test() throws Exception {
    when(pbf.create(jobRoot, IMAGE_NAME, "--config", WorkerConstants.TARGET_CONFIG_JSON_FILENAME)
        .redirectError(jobRoot.resolve(WorkerConstants.TARGET_ERR_LOG).toFile())
        .start()).thenReturn(process);
    when(process.getOutputStream()).thenReturn(outputStream);

    final StandardTargetConfig targetConfig =
        WorkerUtils.syncToTargetConfig(TestConfigHelpers.createSyncConfig().getValue());

    final SingerTarget target = new DefaultSingerTarget(IMAGE_NAME, pbf);
    target.start(targetConfig, jobRoot);

    SingerMessage recordMessage = SingerMessageUtils.createRecordMessage(TABLE_NAME, COLUMN_NAME, "blue");
    target.accept(recordMessage);
    target.close();

    String actualOutput = new String(outputStream.toByteArray());
    assertEquals(Jsons.serialize(recordMessage) + "\n", actualOutput);
  }

}
