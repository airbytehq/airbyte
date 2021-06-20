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

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.TestConfigHelpers;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultAirbyteDestinationTest {

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final String JOB_ROOT_PREFIX = "workspace";
  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";

  private static final WorkerDestinationConfig DESTINATION_CONFIG =
      WorkerUtils.syncToWorkerDestinationConfig(TestConfigHelpers.createSyncConfig().getValue());

  private static final List<AirbyteMessage> MESSAGES = Lists.newArrayList(
      AirbyteMessageUtils.createStateMessage("checkpoint", "1"),
      AirbyteMessageUtils.createStateMessage("checkpoint", "2"));

  private Path jobRoot;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private AirbyteStreamFactory streamFactory;
  private ByteArrayOutputStream outputStream;

  @BeforeEach
  public void setup() throws IOException, WorkerException {
    jobRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), JOB_ROOT_PREFIX);

    process = mock(Process.class);
    outputStream = spy(new ByteArrayOutputStream());
    when(process.getOutputStream()).thenReturn(outputStream);
    when(process.getInputStream()).thenReturn(new ByteArrayInputStream("input".getBytes(StandardCharsets.UTF_8)));
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream("error".getBytes(StandardCharsets.UTF_8)));

    integrationLauncher = mock(IntegrationLauncher.class, RETURNS_DEEP_STUBS);
    final InputStream inputStream = mock(InputStream.class);
    when(integrationLauncher.write(
        jobRoot,
        WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
        Jsons.serialize(DESTINATION_CONFIG.getDestinationConnectionConfiguration()),
        WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME,
        Jsons.serialize(DESTINATION_CONFIG.getCatalog())))
            .thenReturn(process);

    when(process.isAlive()).thenReturn(true);
    when(process.getInputStream()).thenReturn(inputStream);

    streamFactory = noop -> MESSAGES.stream();
  }

  @SuppressWarnings("BusyWait")
  @Test
  public void testSuccessfulLifecycle() throws Exception {
    final AirbyteDestination destination = new DefaultAirbyteDestination(integrationLauncher, streamFactory);
    destination.start(DESTINATION_CONFIG, jobRoot);

    final AirbyteMessage recordMessage = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "blue");
    destination.accept(recordMessage);

    final List<AirbyteMessage> messages = Lists.newArrayList();

    assertFalse(destination.isFinished());
    messages.add(destination.attemptRead().get());
    assertFalse(destination.isFinished());
    messages.add(destination.attemptRead().get());
    assertFalse(destination.isFinished());

    when(process.isAlive()).thenReturn(false);
    assertTrue(destination.isFinished());

    verify(outputStream, never()).close();

    destination.notifyEndOfStream();

    verify(outputStream).close();

    destination.close();

    Assertions.assertEquals(MESSAGES, messages);

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).waitFor(anyLong(), any());
  }

  @Test
  public void testCloseNotifiesLifecycle() throws Exception {
    final AirbyteDestination destination = new DefaultAirbyteDestination(integrationLauncher);
    destination.start(DESTINATION_CONFIG, jobRoot);

    verify(outputStream, never()).close();

    when(process.isAlive()).thenReturn(false);
    destination.close();
    verify(outputStream).close();
  }

}
