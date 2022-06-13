/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import static java.lang.Thread.sleep;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.atLeastOnce;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.ReplicationAttemptSummary;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
import io.airbyte.config.State;
import io.airbyte.config.StreamSyncStats;
import io.airbyte.config.SyncStats;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.workers.*;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.helper.FailureHelper;
import io.airbyte.workers.internal.AirbyteDestination;
import io.airbyte.workers.internal.AirbyteMessageTracker;
import io.airbyte.workers.internal.AirbyteMessageUtils;
import io.airbyte.workers.internal.AirbyteSource;
import io.airbyte.workers.internal.NamespacingMapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicReference;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.mockito.Mockito;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

class DefaultReplicationWorkerTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultReplicationWorkerTest.class);

  private static final String JOB_ID = "0";
  private static final int JOB_ATTEMPT = 0;
  private static final Path WORKSPACE_ROOT = Path.of("workspaces/10");
  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";
  private static final AirbyteMessage RECORD_MESSAGE1 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "blue");
  private static final AirbyteMessage RECORD_MESSAGE2 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow");
  private static final AirbyteMessage RECORD_MESSAGE3 = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, 3);
  private static final AirbyteMessage STATE_MESSAGE = AirbyteMessageUtils.createStateMessage("checkpoint", "1");
  private static final AirbyteTraceMessage ERROR_TRACE_MESSAGE =
      AirbyteMessageUtils.createErrorTraceMessage("a connector error occurred", Double.valueOf(123));

  private Path jobRoot;
  private AirbyteSource source;
  private NamespacingMapper mapper;
  private AirbyteDestination destination;
  private StandardSyncInput syncInput;
  private WorkerSourceConfig sourceConfig;
  private WorkerDestinationConfig destinationConfig;
  private AirbyteMessageTracker messageTracker;
  private RecordSchemaValidator recordSchemaValidator;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws Exception {
    MDC.clear();

    jobRoot = Files.createDirectories(Files.createTempDirectory("test").resolve(WORKSPACE_ROOT));

    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig();
    syncInput = syncPair.getValue();

    sourceConfig = WorkerUtils.syncToWorkerSourceConfig(syncInput);
    destinationConfig = WorkerUtils.syncToWorkerDestinationConfig(syncInput);

    source = mock(AirbyteSource.class);
    mapper = mock(NamespacingMapper.class);
    destination = mock(AirbyteDestination.class);
    messageTracker = mock(AirbyteMessageTracker.class);
    recordSchemaValidator = mock(RecordSchemaValidator.class);

    when(source.isFinished()).thenReturn(false, false, false, true);
    when(destination.isFinished()).thenReturn(false, false, false, true);
    when(source.attemptRead()).thenReturn(Optional.of(RECORD_MESSAGE1), Optional.empty(), Optional.of(RECORD_MESSAGE2));
    when(destination.attemptRead()).thenReturn(Optional.of(STATE_MESSAGE));
    when(mapper.mapCatalog(destinationConfig.getCatalog())).thenReturn(destinationConfig.getCatalog());
    when(mapper.mapMessage(RECORD_MESSAGE1)).thenReturn(RECORD_MESSAGE1);
    when(mapper.mapMessage(RECORD_MESSAGE2)).thenReturn(RECORD_MESSAGE2);
    when(mapper.mapMessage(RECORD_MESSAGE3)).thenReturn(RECORD_MESSAGE3);
  }

  @AfterEach
  void tearDown() {
    MDC.clear();
  }

  @Test
  void test() throws Exception {
    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    worker.run(syncInput, jobRoot);

    verify(source).start(sourceConfig, jobRoot);
    verify(destination).start(destinationConfig, jobRoot);
    verify(destination).accept(RECORD_MESSAGE1);
    verify(destination).accept(RECORD_MESSAGE2);
    verify(source, atLeastOnce()).close();
    verify(destination).close();
    verify(recordSchemaValidator).validateSchema(RECORD_MESSAGE1.getRecord(), STREAM_NAME);
    verify(recordSchemaValidator).validateSchema(RECORD_MESSAGE2.getRecord(), STREAM_NAME);
  }

  @Test
  void testInvalidSchema() throws Exception {
    when(source.attemptRead()).thenReturn(Optional.of(RECORD_MESSAGE1), Optional.of(RECORD_MESSAGE2), Optional.of(RECORD_MESSAGE3));

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    worker.run(syncInput, jobRoot);

    verify(source).start(sourceConfig, jobRoot);
    verify(destination).start(destinationConfig, jobRoot);
    verify(destination).accept(RECORD_MESSAGE1);
    verify(destination).accept(RECORD_MESSAGE2);
    verify(recordSchemaValidator).validateSchema(RECORD_MESSAGE1.getRecord(), STREAM_NAME);
    verify(recordSchemaValidator).validateSchema(RECORD_MESSAGE2.getRecord(), STREAM_NAME);
    verify(recordSchemaValidator).validateSchema(RECORD_MESSAGE3.getRecord(), STREAM_NAME);
    verify(source).close();
    verify(destination).close();
  }

  @Test
  void testSourceNonZeroExitValue() throws Exception {
    when(source.getExitValue()).thenReturn(1);
    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);
    final ReplicationOutput output = worker.run(syncInput, jobRoot);
    assertEquals(ReplicationStatus.FAILED, output.getReplicationAttemptSummary().getStatus());
    assertTrue(output.getFailures().stream().anyMatch(f -> f.getFailureOrigin().equals(FailureOrigin.SOURCE)));
  }

  @Test
  void testReplicationRunnableSourceFailure() throws Exception {
    final String SOURCE_ERROR_MESSAGE = "the source had a failure";

    when(source.attemptRead()).thenThrow(new RuntimeException(SOURCE_ERROR_MESSAGE));

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final ReplicationOutput output = worker.run(syncInput, jobRoot);
    assertEquals(ReplicationStatus.FAILED, output.getReplicationAttemptSummary().getStatus());
    assertTrue(output.getFailures().stream()
        .anyMatch(f -> f.getFailureOrigin().equals(FailureOrigin.SOURCE) && f.getStacktrace().contains(SOURCE_ERROR_MESSAGE)));
  }

  @Test
  void testReplicationRunnableDestinationFailure() throws Exception {
    final String DESTINATION_ERROR_MESSAGE = "the destination had a failure";

    doThrow(new RuntimeException(DESTINATION_ERROR_MESSAGE)).when(destination).accept(Mockito.any());

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final ReplicationOutput output = worker.run(syncInput, jobRoot);
    assertEquals(ReplicationStatus.FAILED, output.getReplicationAttemptSummary().getStatus());
    assertTrue(output.getFailures().stream()
        .anyMatch(f -> f.getFailureOrigin().equals(FailureOrigin.DESTINATION) && f.getStacktrace().contains(DESTINATION_ERROR_MESSAGE)));
  }

  @Test
  void testReplicationRunnableDestinationFailureViaTraceMessage() throws Exception {
    final FailureReason failureReason = FailureHelper.destinationFailure(ERROR_TRACE_MESSAGE, Long.valueOf(JOB_ID), JOB_ATTEMPT);
    when(messageTracker.errorTraceMessageFailure(Long.valueOf(JOB_ID), JOB_ATTEMPT)).thenReturn(failureReason);

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final ReplicationOutput output = worker.run(syncInput, jobRoot);
    assertTrue(output.getFailures().stream()
        .anyMatch(f -> f.getFailureOrigin().equals(FailureOrigin.DESTINATION)
            && f.getExternalMessage().contains(ERROR_TRACE_MESSAGE.getError().getMessage())));
  }

  @Test
  void testReplicationRunnableWorkerFailure() throws Exception {
    final String WORKER_ERROR_MESSAGE = "the worker had a failure";

    doThrow(new RuntimeException(WORKER_ERROR_MESSAGE)).when(messageTracker).acceptFromSource(Mockito.any());

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final ReplicationOutput output = worker.run(syncInput, jobRoot);
    assertEquals(ReplicationStatus.FAILED, output.getReplicationAttemptSummary().getStatus());
    assertTrue(output.getFailures().stream()
        .anyMatch(f -> f.getFailureOrigin().equals(FailureOrigin.REPLICATION) && f.getStacktrace().contains(WORKER_ERROR_MESSAGE)));
  }

  @Test
  void testDestinationNonZeroExitValue() throws Exception {
    when(destination.getExitValue()).thenReturn(1);

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final ReplicationOutput output = worker.run(syncInput, jobRoot);
    assertEquals(ReplicationStatus.FAILED, output.getReplicationAttemptSummary().getStatus());
    assertTrue(output.getFailures().stream().anyMatch(f -> f.getFailureOrigin().equals(FailureOrigin.DESTINATION)));
  }

  @Test
  void testDestinationRunnableDestinationFailure() throws Exception {
    final String DESTINATION_ERROR_MESSAGE = "the destination had a failure";

    doThrow(new RuntimeException(DESTINATION_ERROR_MESSAGE)).when(destination).notifyEndOfInput();

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final ReplicationOutput output = worker.run(syncInput, jobRoot);
    assertEquals(ReplicationStatus.FAILED, output.getReplicationAttemptSummary().getStatus());
    assertTrue(output.getFailures().stream()
        .anyMatch(f -> f.getFailureOrigin().equals(FailureOrigin.DESTINATION) && f.getStacktrace().contains(DESTINATION_ERROR_MESSAGE)));
  }

  @Test
  void testDestinationRunnableWorkerFailure() throws Exception {
    final String WORKER_ERROR_MESSAGE = "the worker had a failure";

    doThrow(new RuntimeException(WORKER_ERROR_MESSAGE)).when(messageTracker).acceptFromDestination(Mockito.any());

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final ReplicationOutput output = worker.run(syncInput, jobRoot);
    assertEquals(ReplicationStatus.FAILED, output.getReplicationAttemptSummary().getStatus());
    assertTrue(output.getFailures().stream()
        .anyMatch(f -> f.getFailureOrigin().equals(FailureOrigin.REPLICATION) && f.getStacktrace().contains(WORKER_ERROR_MESSAGE)));
  }

  @Test
  void testLoggingInThreads() throws IOException, WorkerException {
    // set up the mdc so that actually log to a file, so that we can verify that file logging captures
    // threads.
    final Path jobRoot = Files.createTempDirectory(Path.of("/tmp"), "mdc_test");
    LogClientSingleton.getInstance().setJobMdc(WorkerEnvironment.DOCKER, LogConfigs.EMPTY, jobRoot);

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    worker.run(syncInput, jobRoot);

    final Path logPath = jobRoot.resolve(LogClientSingleton.LOG_FILENAME);
    final String logs = IOs.readFile(logPath);

    // make sure we get logs from the threads.
    assertTrue(logs.contains("Replication thread started."));
    assertTrue(logs.contains("Destination output thread started."));
  }

  @Test
  void testLogMaskRegex() throws IOException {
    final Path jobRoot = Files.createTempDirectory(Path.of("/tmp"), "mdc_test");
    MDC.put(LogClientSingleton.WORKSPACE_MDC_KEY, jobRoot.toString());

    LOGGER.info(
        "500 Server Error: Internal Server Error for url: https://api.hubapi.com/crm/v3/objects/contact?limit=100&archived=false&hapikey=secret-key_1&after=5315621");

    final Path logPath = jobRoot.resolve("logs.log");
    final String logs = IOs.readFile(logPath);
    assertTrue(logs.contains("apikey"));
    assertFalse(logs.contains("secret-key_1"));
  }

  @SuppressWarnings({"BusyWait"})
  @Test
  void testCancellation() throws InterruptedException {
    final AtomicReference<ReplicationOutput> output = new AtomicReference<>();
    when(source.isFinished()).thenReturn(false);
    when(messageTracker.getDestinationOutputState()).thenReturn(Optional.of(new State().withState(STATE_MESSAGE.getState().getData())));

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final Thread workerThread = new Thread(() -> {
      try {
        output.set(worker.run(syncInput, jobRoot));
      } catch (final WorkerException e) {
        throw new RuntimeException(e);
      }
    });

    workerThread.start();

    // verify the worker is actually running before we kill it.
    while (Mockito.mockingDetails(messageTracker).getInvocations().size() < 5) {
      LOGGER.info("waiting for worker to start running");
      sleep(100);
    }

    worker.cancel();
    Assertions.assertTimeout(Duration.ofSeconds(5), (Executable) workerThread::join);
    assertNotNull(output.get());
    assertEquals(output.get().getState().getState(), STATE_MESSAGE.getState().getData());
  }

  @Test
  void testPopulatesOutputOnSuccess() throws WorkerException {
    final JsonNode expectedState = Jsons.jsonNode(ImmutableMap.of("updated_at", 10L));
    when(messageTracker.getDestinationOutputState()).thenReturn(Optional.of(new State().withState(expectedState)));
    when(messageTracker.getTotalRecordsEmitted()).thenReturn(12L);
    when(messageTracker.getTotalBytesEmitted()).thenReturn(100L);
    when(messageTracker.getTotalStateMessagesEmitted()).thenReturn(3L);
    when(messageTracker.getStreamToEmittedBytes()).thenReturn(Collections.singletonMap("stream1", 100L));
    when(messageTracker.getStreamToEmittedRecords()).thenReturn(Collections.singletonMap("stream1", 12L));

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final ReplicationOutput actual = worker.run(syncInput, jobRoot);
    final ReplicationOutput replicationOutput = new ReplicationOutput()
        .withReplicationAttemptSummary(new ReplicationAttemptSummary()
            .withRecordsSynced(12L)
            .withBytesSynced(100L)
            .withStatus(ReplicationStatus.COMPLETED)
            .withTotalStats(new SyncStats()
                .withRecordsEmitted(12L)
                .withBytesEmitted(100L)
                .withStateMessagesEmitted(3L)
                .withRecordsCommitted(12L)) // since success, should use emitted count
            .withStreamStats(Collections.singletonList(
                new StreamSyncStats()
                    .withStreamName("stream1")
                    .withStats(new SyncStats()
                        .withBytesEmitted(100L)
                        .withRecordsEmitted(12L)
                        .withRecordsCommitted(12L) // since success, should use emitted count
                        .withStateMessagesEmitted(null)))))
        .withOutputCatalog(syncInput.getCatalog())
        .withState(new State().withState(expectedState));

    // good enough to verify that times are present.
    assertNotNull(actual.getReplicationAttemptSummary().getStartTime());
    assertNotNull(actual.getReplicationAttemptSummary().getEndTime());

    // verify output object matches declared json schema spec.
    final Set<String> validate = new JsonSchemaValidator()
        .validate(Jsons.jsonNode(Jsons.jsonNode(JsonSchemaValidator.getSchema(ConfigSchema.REPLICATION_OUTPUT.getConfigSchemaFile()))),
            Jsons.jsonNode(actual));
    assertTrue(validate.isEmpty(), "Validation errors: " + Strings.join(validate, ","));

    // remove times so we can do the rest of the object <> object comparison.
    actual.getReplicationAttemptSummary().withStartTime(null);
    actual.getReplicationAttemptSummary().withEndTime(null);

    assertEquals(replicationOutput, actual);
  }

  @Test
  void testPopulatesStateOnFailureIfAvailable() throws Exception {
    doThrow(new IllegalStateException("induced exception")).when(source).close();
    when(messageTracker.getDestinationOutputState()).thenReturn(Optional.of(new State().withState(STATE_MESSAGE.getState().getData())));

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final ReplicationOutput actual = worker.run(syncInput, jobRoot);
    assertNotNull(actual);
    assertEquals(STATE_MESSAGE.getState().getData(), actual.getState().getState());
  }

  @Test
  void testRetainsStateOnFailureIfNewStateNotAvailable() throws Exception {
    doThrow(new IllegalStateException("induced exception")).when(source).close();

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final ReplicationOutput actual = worker.run(syncInput, jobRoot);

    assertNotNull(actual);
    assertEquals(syncInput.getState().getState(), actual.getState().getState());
  }

  @Test
  void testPopulatesStatsOnFailureIfAvailable() throws Exception {
    doThrow(new IllegalStateException("induced exception")).when(source).close();
    when(messageTracker.getTotalRecordsEmitted()).thenReturn(12L);
    when(messageTracker.getTotalBytesEmitted()).thenReturn(100L);
    when(messageTracker.getTotalRecordsCommitted()).thenReturn(Optional.of(6L));
    when(messageTracker.getTotalStateMessagesEmitted()).thenReturn(3L);
    when(messageTracker.getStreamToEmittedBytes()).thenReturn(Collections.singletonMap("stream1", 100L));
    when(messageTracker.getStreamToEmittedRecords()).thenReturn(Collections.singletonMap("stream1", 12L));
    when(messageTracker.getStreamToCommittedRecords()).thenReturn(Optional.of(Collections.singletonMap("stream1", 6L)));

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final ReplicationOutput actual = worker.run(syncInput, jobRoot);
    final SyncStats expectedTotalStats = new SyncStats()
        .withRecordsEmitted(12L)
        .withBytesEmitted(100L)
        .withStateMessagesEmitted(3L)
        .withRecordsCommitted(6L);
    final List<StreamSyncStats> expectedStreamStats = Collections.singletonList(
        new StreamSyncStats()
            .withStreamName("stream1")
            .withStats(new SyncStats()
                .withBytesEmitted(100L)
                .withRecordsEmitted(12L)
                .withRecordsCommitted(6L)
                .withStateMessagesEmitted(null)));

    assertNotNull(actual);
    assertEquals(expectedTotalStats, actual.getReplicationAttemptSummary().getTotalStats());
    assertEquals(expectedStreamStats, actual.getReplicationAttemptSummary().getStreamStats());
  }

  @Test
  void testDoesNotPopulatesStateOnFailureIfNotAvailable() throws Exception {
    final StandardSyncInput syncInputWithoutState = Jsons.clone(syncInput);
    syncInputWithoutState.setState(null);

    doThrow(new IllegalStateException("induced exception")).when(source).close();

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);

    final ReplicationOutput actual = worker.run(syncInputWithoutState, jobRoot);

    assertNotNull(actual);
    assertNull(actual.getState());
  }

  @Test
  void testDoesNotPopulateOnIrrecoverableFailure() {
    doThrow(new IllegalStateException("induced exception")).when(messageTracker).getTotalRecordsEmitted();

    final ReplicationWorker worker = new DefaultReplicationWorker(
        JOB_ID,
        JOB_ATTEMPT,
        source,
        mapper,
        destination,
        messageTracker,
        recordSchemaValidator);
    assertThrows(WorkerException.class, () -> worker.run(syncInput, jobRoot));
  }

}
