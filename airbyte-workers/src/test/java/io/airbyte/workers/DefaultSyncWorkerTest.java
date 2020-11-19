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

package io.airbyte.workers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.workers.protocols.airbyte.AirbyteDestination;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageTracker;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageUtils;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultSyncWorkerTest {

  private static final Path WORKSPACE_ROOT = Path.of("workspaces/10");
  private static final String STREAM_NAME = "user_preferences";
  private static final String INVALID_STREAM_NAME = "invalid stream name";
  private static final String FIELD_NAME = "favorite_color";
  private static final AirbyteMessage RECORD_MESSAGE1 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "blue");
  private static final AirbyteMessage RECORD_MESSAGE2 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow");
  private static final AirbyteMessage INVALID_RECORD_MESSAGE = AirbyteMessageUtils.createRecordMessage(INVALID_STREAM_NAME, FIELD_NAME, "yellow");

  private Path jobRoot;
  private Path normalizationRoot;
  private AirbyteSource tap;
  private AirbyteDestination target;
  private StandardSyncInput invalidSyncInput;
  private StandardTapConfig tapConfig;
  private StandardTargetConfig targetConfig;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws Exception {
    jobRoot = Files.createDirectories(Files.createTempDirectory("test").resolve(WORKSPACE_ROOT));
    normalizationRoot = jobRoot.resolve("normalize");

    final StandardSyncInput validSyncInput = TestConfigHelpers.createSyncConfig().getValue();

    // create sync input with invalid stream to ensure it is filtered out
    invalidSyncInput = new StandardSyncInput();
    invalidSyncInput.setConnectionId(validSyncInput.getConnectionId());
    invalidSyncInput.setDestinationConnection(validSyncInput.getDestinationConnection());
    invalidSyncInput.setSourceConnection(validSyncInput.getSourceConnection());
    invalidSyncInput.setState(validSyncInput.getState());
    invalidSyncInput.setSyncMode(validSyncInput.getSyncMode());

    final ConfiguredAirbyteStream invalidStream = new ConfiguredAirbyteStream();
    invalidStream.setName(INVALID_STREAM_NAME);
    invalidStream.setJsonSchema(Jsons.deserialize("{}"));
    final List<ConfiguredAirbyteStream> streams = new ArrayList<>(validSyncInput.getCatalog().getStreams());
    streams.add(invalidStream);
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog();
    catalog.setStreams(streams);
    invalidSyncInput.setCatalog(catalog);

    tapConfig = WorkerUtils.syncToTapConfig(validSyncInput);
    targetConfig = WorkerUtils.syncToTargetConfig(validSyncInput);

    tap = mock(AirbyteSource.class);
    target = mock(AirbyteDestination.class);

    when(tap.isFinished()).thenReturn(false, false, false, false, true);
    when(tap.attemptRead()).thenReturn(Optional.of(RECORD_MESSAGE1), Optional.empty(), Optional.of(RECORD_MESSAGE2),
        Optional.of(INVALID_RECORD_MESSAGE));
  }

  @Test
  void test() throws Exception {
    final DefaultSyncWorker defaultSyncWorker =
        new DefaultSyncWorker(tap, target, new AirbyteMessageTracker());
    final OutputAndStatus<StandardSyncOutput> run = defaultSyncWorker.run(invalidSyncInput, jobRoot);

    assertEquals(JobStatus.SUCCEEDED, run.getStatus());

    verify(tap).start(tapConfig, jobRoot);
    verify(target).start(targetConfig, jobRoot);
    verify(target).accept(RECORD_MESSAGE1);
    verify(target).accept(RECORD_MESSAGE2);
    verify(tap).close();
    verify(target).close();
  }

}
