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
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardSyncSummary.Status;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.normalization.NormalizationRunner;
import io.airbyte.workers.protocols.MessageTracker;
import io.airbyte.workers.protocols.airbyte.AirbyteDestination;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageTracker;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageUtils;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.NamespacingMapper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultSyncWorkerTest {

  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;
  private static final Path WORKSPACE_ROOT = Path.of("workspaces/10");
  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";
  private static final AirbyteMessage RECORD_MESSAGE1 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "blue");
  private static final AirbyteMessage RECORD_MESSAGE2 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow");

  private Path jobRoot;
  private Path normalizationRoot;
  private AirbyteSource tap;
  private NamespacingMapper mapper;
  private AirbyteDestination target;
  private StandardSyncInput syncInput;
  private StandardTapConfig tapConfig;
  private StandardTargetConfig targetConfig;
  private NormalizationRunner normalizationRunner;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws Exception {
    jobRoot = Files.createDirectories(Files.createTempDirectory("test").resolve(WORKSPACE_ROOT));
    normalizationRoot = jobRoot.resolve("normalize");

    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig();
    syncInput = syncPair.getValue();

    tapConfig = WorkerUtils.syncToTapConfig(syncInput);
    targetConfig = WorkerUtils.syncToTargetConfig(syncInput);

    tap = mock(AirbyteSource.class);
    mapper = mock(NamespacingMapper.class);
    target = mock(AirbyteDestination.class);
    normalizationRunner = mock(NormalizationRunner.class);

    when(tap.isFinished()).thenReturn(false, false, false, true);
    when(tap.attemptRead()).thenReturn(Optional.of(RECORD_MESSAGE1), Optional.empty(), Optional.of(RECORD_MESSAGE2));
    when(mapper.mapCatalog(targetConfig.getCatalog())).thenReturn(targetConfig.getCatalog());
    when(mapper.mapMessage(RECORD_MESSAGE1)).thenReturn(RECORD_MESSAGE1);
    when(mapper.mapMessage(RECORD_MESSAGE2)).thenReturn(RECORD_MESSAGE2);
    when(normalizationRunner.normalize(JOB_ID, JOB_ATTEMPT, normalizationRoot, targetConfig.getDestinationConnectionConfiguration(),
        targetConfig.getCatalog()))
            .thenReturn(true);
  }

  @Test
  void test() throws Exception {
    final DefaultSyncWorker defaultSyncWorker =
        new DefaultSyncWorker(JOB_ID, JOB_ATTEMPT, tap, mapper, target, new AirbyteMessageTracker(), normalizationRunner);

    defaultSyncWorker.run(syncInput, jobRoot);

    verify(tap).start(tapConfig, jobRoot);
    verify(target).start(targetConfig, jobRoot);
    verify(target).accept(RECORD_MESSAGE1);
    verify(target).accept(RECORD_MESSAGE2);
    verify(normalizationRunner).start();
    verify(normalizationRunner).normalize(JOB_ID, JOB_ATTEMPT, normalizationRoot, targetConfig.getDestinationConnectionConfiguration(),
        targetConfig.getCatalog());
    verify(normalizationRunner).close();
    verify(tap).close();
    verify(target).close();
  }

  @SuppressWarnings("unchecked")
  @Test
  void testPopulatesSyncSummary() throws WorkerException {
    final MessageTracker<AirbyteMessage> messageTracker = mock(MessageTracker.class);
    final JsonNode expectedState = Jsons.jsonNode(ImmutableMap.of("updated_at", 10L));
    when(messageTracker.getRecordCount()).thenReturn(12L);
    when(messageTracker.getBytesCount()).thenReturn(100L);
    when(messageTracker.getOutputState()).thenReturn(Optional.of(expectedState));

    final DefaultSyncWorker defaultSyncWorker = new DefaultSyncWorker(JOB_ID, JOB_ATTEMPT, tap, mapper, target, messageTracker, normalizationRunner);
    final StandardSyncOutput actual = defaultSyncWorker.run(syncInput, jobRoot);
    final StandardSyncOutput expectedSyncOutput = new StandardSyncOutput()
        .withStandardSyncSummary(new StandardSyncSummary()
            .withRecordsSynced(12L)
            .withBytesSynced(100L)
            .withStatus(Status.COMPLETED))
        .withState(new State().withState(expectedState));

    // good enough to verify that times are present.
    assertNotNull(actual.getStandardSyncSummary().getStartTime());
    assertNotNull(actual.getStandardSyncSummary().getEndTime());
    // remove times so we can do the rest of the object <> object comparison.
    actual.getStandardSyncSummary().withStartTime(null);
    actual.getStandardSyncSummary().withEndTime(null);

    assertEquals(expectedSyncOutput, actual);
  }

}
