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

package io.airbyte.workers.normalization;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.normalization.DefaultNormalizationRunner.DestinationType;
import io.airbyte.workers.process.ProcessFactory;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultNormalizationRunnerTest {

  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;

  private Path jobRoot;
  private ProcessFactory processFactory;
  private Process process;
  private JsonNode config;
  private ConfiguredAirbyteCatalog catalog;

  @BeforeEach
  void setup() throws IOException, WorkerException {
    jobRoot = Files.createDirectories(Files.createTempDirectory("test"));
    processFactory = mock(ProcessFactory.class);
    process = mock(Process.class);

    config = mock(JsonNode.class);
    catalog = mock(ConfiguredAirbyteCatalog.class);

    final Map<String, String> files = ImmutableMap.of(
        WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME, Jsons.serialize(config),
        WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME, Jsons.serialize(catalog));

    when(processFactory.create(JOB_ID, JOB_ATTEMPT, jobRoot, DefaultNormalizationRunner.NORMALIZATION_IMAGE_NAME, false, files, null,
        WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS,
        "run",
        "--integration-type", "bigquery",
        "--config", WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
        "--catalog", WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME))
            .thenReturn(process);
    when(process.getInputStream()).thenReturn(new ByteArrayInputStream("hello".getBytes()));
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream("hello".getBytes()));
  }

  @Test
  void test() throws Exception {
    final NormalizationRunner runner = new DefaultNormalizationRunner(DestinationType.BIGQUERY, processFactory);

    when(process.exitValue()).thenReturn(0);

    assertTrue(runner.normalize(JOB_ID, JOB_ATTEMPT, jobRoot, config, catalog, WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS));
  }

  @Test
  public void testClose() throws Exception {
    when(process.isAlive()).thenReturn(true).thenReturn(false);

    final NormalizationRunner runner = new DefaultNormalizationRunner(DestinationType.BIGQUERY, processFactory);
    runner.normalize(JOB_ID, JOB_ATTEMPT, jobRoot, config, catalog, WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);
    runner.close();

    verify(process).waitFor();
  }

  @Test
  public void testFailure() {
    doThrow(new RuntimeException()).when(process).exitValue();

    final NormalizationRunner runner = new DefaultNormalizationRunner(DestinationType.BIGQUERY, processFactory);
    assertThrows(RuntimeException.class,
        () -> runner.normalize(JOB_ID, JOB_ATTEMPT, jobRoot, config, catalog, WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS));

    verify(process).destroy();
  }

}
