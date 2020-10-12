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

package io.airbyte.workers.protocols.airbyte;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.workers.DiscoverCatalogWorker;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
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

class DefaultAirbyteSourceTest {

  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";

  private static final AirbyteCatalog CATALOG = new AirbyteCatalog()
      .withStreams(Collections.singletonList(
          new AirbyteStream()
              .withName("hudi:latest")
              .withSchema(Jsons.deserialize("{}"))));

  private static final StandardTapConfig TAP_CONFIG = WorkerUtils.syncToTapConfig(TestConfigHelpers.createSyncConfig().getValue());
  private static final StandardDiscoverCatalogInput DISCOVER_SCHEMA_INPUT = new StandardDiscoverCatalogInput()
      .withConnectionConfiguration(TAP_CONFIG.getSourceConnectionImplementation().getConfiguration());

  final List<AirbyteMessage> MESSAGES = Lists.newArrayList(
      AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "blue"),
      AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow"));

  private Path jobRoot;
  private DiscoverCatalogWorker discoverSchemaWorker;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private AirbyteStreamFactory streamFactory;

  @BeforeEach
  public void setup() throws IOException, WorkerException {
    jobRoot = Files.createTempDirectory("test");

    discoverSchemaWorker = mock(DiscoverCatalogWorker.class);
    when(discoverSchemaWorker.run(
        DISCOVER_SCHEMA_INPUT,
        jobRoot.resolve(DefaultAirbyteSource.DISCOVERY_DIR)))
            .thenAnswer(invocation -> {
              Files.writeString(
                  jobRoot.resolve(DefaultAirbyteSource.DISCOVERY_DIR).resolve(WorkerConstants.CATALOG_JSON_FILENAME),
                  Jsons.serialize(CATALOG));
              return new OutputAndStatus<>(JobStatus.SUCCESSFUL, new StandardDiscoverCatalogOutput().withCatalog(CATALOG));
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

    streamFactory = noop -> MESSAGES.stream();
  }

  @SuppressWarnings({"OptionalGetWithoutIsPresent", "BusyWait"})
  @Test
  public void testSuccessfulLifecycle() throws Exception {
    final AirbyteSource tap = new DefaultAirbyteSource(integrationLauncher, streamFactory, discoverSchemaWorker);
    tap.start(TAP_CONFIG, jobRoot);

    final List<AirbyteMessage> messages = Lists.newArrayList();

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
        Jsons.jsonNode(CATALOG),
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
    final AirbyteSource tap = new DefaultAirbyteSource(integrationLauncher, streamFactory, discoverSchemaWorker);
    tap.start(TAP_CONFIG, jobRoot);

    when(process.exitValue()).thenReturn(1);

    Assertions.assertThrows(WorkerException.class, tap::close);
  }

  @Test
  public void testSchemaDiscoveryFail() {
    when(discoverSchemaWorker.run(any(), any())).thenReturn(new OutputAndStatus<>(JobStatus.FAILED));

    final AirbyteSource tap = new DefaultAirbyteSource(integrationLauncher, streamFactory, discoverSchemaWorker);
    Assertions.assertThrows(WorkerException.class, () -> tap.start(TAP_CONFIG, jobRoot));

    assertFalse(Files.exists(jobRoot.resolve(WorkerConstants.TAP_CONFIG_JSON_FILENAME)));
    assertFalse(Files.exists(jobRoot.resolve(WorkerConstants.INPUT_STATE_JSON_FILENAME)));
    assertFalse(Files.exists(jobRoot.resolve(WorkerConstants.CATALOG_JSON_FILENAME)));
  }

}
