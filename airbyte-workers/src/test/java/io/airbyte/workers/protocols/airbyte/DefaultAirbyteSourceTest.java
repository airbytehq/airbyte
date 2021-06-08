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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultAirbyteSourceTest {

  private static final String NAMESPACE = "unused";
  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";

  private static final ConfiguredAirbyteCatalog CATALOG = CatalogHelpers.createConfiguredAirbyteCatalog(
      "hudi:latest",
      NAMESPACE,
      Field.of(FIELD_NAME, JsonSchemaPrimitive.STRING));

  private static final StandardTapConfig SOURCE_CONFIG = new StandardTapConfig()
      .withState(new State().withState(Jsons.jsonNode(ImmutableMap.of("checkpoint", "the future."))))
      .withSourceConnectionConfiguration(Jsons.jsonNode(Map.of(
          "apiKey", "123",
          "region", "us-east")))
      .withCatalog(CatalogHelpers.createConfiguredAirbyteCatalog("hudi:latest", NAMESPACE, Field.of(FIELD_NAME, JsonSchemaPrimitive.STRING)));

  private static final List<AirbyteMessage> MESSAGES = Lists.newArrayList(
      AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "blue"),
      AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow"));

  private Path jobRoot;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private AirbyteStreamFactory streamFactory;
  private HeartbeatMonitor heartbeatMonitor;

  @BeforeEach
  public void setup() throws IOException, WorkerException {
    jobRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "test");

    integrationLauncher = mock(IntegrationLauncher.class, RETURNS_DEEP_STUBS);
    process = mock(Process.class, RETURNS_DEEP_STUBS);
    heartbeatMonitor = mock(HeartbeatMonitor.class);
    final InputStream inputStream = mock(InputStream.class);
    when(integrationLauncher.read(
        jobRoot,
        WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
        WorkerConstants.SOURCE_CATALOG_JSON_FILENAME,
        WorkerConstants.INPUT_STATE_JSON_FILENAME)).thenReturn(process);
    when(process.isAlive()).thenReturn(true);
    when(process.getInputStream()).thenReturn(inputStream);
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream("qwer".getBytes(StandardCharsets.UTF_8)));

    streamFactory = noop -> MESSAGES.stream();
  }

  @SuppressWarnings({"OptionalGetWithoutIsPresent", "BusyWait"})
  @Test
  public void testSuccessfulLifecycle() throws Exception {
    when(heartbeatMonitor.isBeating()).thenReturn(true).thenReturn(false);

    final AirbyteSource source = new DefaultAirbyteSource(integrationLauncher, streamFactory, heartbeatMonitor);
    source.start(SOURCE_CONFIG, jobRoot);

    final List<AirbyteMessage> messages = Lists.newArrayList();

    assertFalse(source.isFinished());
    messages.add(source.attemptRead().get());
    assertFalse(source.isFinished());
    messages.add(source.attemptRead().get());
    assertFalse(source.isFinished());

    when(process.isAlive()).thenReturn(false);
    assertTrue(source.isFinished());
    verify(heartbeatMonitor, times(2)).beat();

    source.close();

    assertEquals(
        Jsons.jsonNode(SOURCE_CONFIG.getSourceConnectionConfiguration()),
        Jsons.deserialize(IOs.readFile(jobRoot, WorkerConstants.SOURCE_CONFIG_JSON_FILENAME)));
    assertEquals(
        Jsons.jsonNode(SOURCE_CONFIG.getState().getState()),
        Jsons.deserialize(IOs.readFile(jobRoot, WorkerConstants.INPUT_STATE_JSON_FILENAME)));
    assertEquals(
        Jsons.jsonNode(CATALOG),
        Jsons.deserialize(IOs.readFile(jobRoot, WorkerConstants.SOURCE_CATALOG_JSON_FILENAME)));

    assertEquals(MESSAGES, messages);

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).exitValue();
  }

}
