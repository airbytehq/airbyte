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

package io.airbyte.workers.protocols.singer;

import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardDiscoverSchemaInput;
import io.airbyte.config.StandardDiscoverSchemaOutput;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.singer.SingerCatalog;
import io.airbyte.singer.SingerMessage;
import io.airbyte.singer.SingerStream;
import io.airbyte.singer.SingerTableSchema;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.SingerDiscoverSchemaWorker;
import io.airbyte.workers.TestConfigHelpers;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class DefaultSingerTapTest {

  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";

  private static final SingerCatalog SINGER_CATALOG = new SingerCatalog()
      .withStreams(Collections.singletonList(new SingerStream()
          .withStream("hudi:latest")
          .withTapStreamId("workspace")
          .withTableName(STREAM_NAME)
          .withSchema(new SingerTableSchema())));

  private static final StandardTapConfig TAP_CONFIG = WorkerUtils.syncToTapConfig(TestConfigHelpers.createSyncConfig().getValue());
  private static final StandardDiscoverSchemaInput DISCOVER_SCHEMA_INPUT = new StandardDiscoverSchemaInput()
      .withConnectionConfiguration(TAP_CONFIG.getSourceConnectionImplementation().getConfiguration());

  final List<SingerMessage> MESSAGES = Lists.newArrayList(
      SingerMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "blue"),
      SingerMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow"));

  private Path jobRoot;
  private SingerDiscoverSchemaWorker discoverSchemaWorker;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private SingerStreamFactory singerStreamFactory;

  @BeforeEach
  public void setup() throws IOException, WorkerException {
    jobRoot = Files.createTempDirectory("test");

    discoverSchemaWorker = mock(SingerDiscoverSchemaWorker.class);
    when(discoverSchemaWorker.run(
        DISCOVER_SCHEMA_INPUT,
        jobRoot.resolve(DefaultSingerTap.DISCOVERY_DIR)))
        .thenAnswer(invocation -> {
          Files.writeString(
              jobRoot.resolve(DefaultSingerTap.DISCOVERY_DIR).resolve(WorkerConstants.CATALOG_JSON_FILENAME),
              Jsons.serialize(SINGER_CATALOG));
          return new OutputAndStatus<>(JobStatus.SUCCESSFUL, new StandardDiscoverSchemaOutput());
        });

    integrationLauncher = mock(IntegrationLauncher.class, RETURNS_DEEP_STUBS);
    process = mock(Process.class, RETURNS_DEEP_STUBS);
    final InputStream inputStream = mock(InputStream.class);
    when(integrationLauncher.read(
        jobRoot,
        WorkerConstants.TAP_CONFIG_JSON_FILENAME,
        WorkerConstants.CATALOG_JSON_FILENAME,
        WorkerConstants.INPUT_STATE_JSON_FILENAME)
        .start()).thenReturn(process);
    when(process.isAlive()).thenReturn(true);
    when(process.getInputStream()).thenReturn(inputStream);
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream("qwer".getBytes(StandardCharsets.UTF_8)));

    singerStreamFactory = noop -> MESSAGES.stream();
  }

  @SuppressWarnings({"OptionalGetWithoutIsPresent", "BusyWait"})
  @Test
  public void testSuccessfulLifecycle() throws Exception {
    final SingerTap tap = new DefaultSingerTap(integrationLauncher, singerStreamFactory, discoverSchemaWorker);
    tap.start(TAP_CONFIG, jobRoot);

    final List<SingerMessage> messages = Lists.newArrayList();

    assertFalse(tap.isFinished());
    messages.add(tap.attemptRead().get());
    assertFalse(tap.isFinished());
    messages.add(tap.attemptRead().get());
    assertFalse(tap.isFinished());

    when(process.isAlive()).thenReturn(false);
    assertTrue(tap.isFinished());

    tap.close();

    assertEquals(
        Jsons.jsonNode(TAP_CONFIG.getSourceConnectionImplementation().getConfiguration()),
        Jsons.deserialize(IOs.readFile(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME)));
    assertEquals(
        Jsons.jsonNode(TAP_CONFIG.getState()),
        Jsons.deserialize(IOs.readFile(jobRoot, WorkerConstants.INPUT_STATE_JSON_FILENAME)));
    assertEquals(
        Jsons.jsonNode(SINGER_CATALOG),
        Jsons.deserialize(IOs.readFile(jobRoot, WorkerConstants.CATALOG_JSON_FILENAME)));

    assertEquals(MESSAGES, messages);

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).waitFor(anyLong(), any());
  }

  @Test
  public void testProcessFail() throws Exception {
    final SingerTap tap = new DefaultSingerTap(integrationLauncher, singerStreamFactory, discoverSchemaWorker);
    tap.start(TAP_CONFIG, jobRoot);

    when(process.exitValue()).thenReturn(1);

    Assertions.assertThrows(WorkerException.class, tap::close);
  }

  @Test
  public void testSchemaDiscoveryFail() {
    when(discoverSchemaWorker.run(any(), any())).thenReturn(new OutputAndStatus<>(JobStatus.FAILED));

    final SingerTap tap = new DefaultSingerTap(integrationLauncher, singerStreamFactory, discoverSchemaWorker);
    Assertions.assertThrows(WorkerException.class, () -> tap.start(TAP_CONFIG, jobRoot));

    assertFalse(Files.exists(jobRoot.resolve(WorkerConstants.TAP_CONFIG_JSON_FILENAME)));
    assertFalse(Files.exists(jobRoot.resolve(WorkerConstants.INPUT_STATE_JSON_FILENAME)));
    assertFalse(Files.exists(jobRoot.resolve(WorkerConstants.CATALOG_JSON_FILENAME)));
  }

}
