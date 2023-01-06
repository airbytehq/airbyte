/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static io.airbyte.commons.logging.LoggingHelper.RESET;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.LoggingHelper.Color;
import io.airbyte.commons.protocol.DefaultProtocolSerializer;
import io.airbyte.commons.protocol.ProtocolSerializer;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import io.airbyte.workers.test_utils.TestConfigHelpers;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class DefaultAirbyteDestinationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultAirbyteDestinationTest.class);
  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final String JOB_ROOT_PREFIX = "workspace";
  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";

  private static final WorkerDestinationConfig DESTINATION_CONFIG =
      WorkerUtils.syncToWorkerDestinationConfig(TestConfigHelpers.createSyncConfig().getValue());

  private static final List<AirbyteMessage> MESSAGES = Lists.newArrayList(
      AirbyteMessageUtils.createStateMessage("checkpoint", "1"),
      AirbyteMessageUtils.createStateMessage("checkpoint", "2"));

  private static Path logJobRoot;

  static {
    try {
      logJobRoot = Files.createTempDirectory(Path.of("/tmp"), "mdc_test");
      LogClientSingleton.getInstance().setJobMdc(WorkerEnvironment.DOCKER, LogConfigs.EMPTY, logJobRoot);
    } catch (final IOException e) {
      LOGGER.error(e.toString());
    }
  }

  private Path jobRoot;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private AirbyteStreamFactory streamFactory;
  private AirbyteMessageBufferedWriterFactory messageWriterFactory;
  private final ProtocolSerializer protocolSerializer = new DefaultProtocolSerializer();
  private ByteArrayOutputStream outputStream;

  @BeforeEach
  void setup() throws IOException, WorkerException {
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
    messageWriterFactory = new DefaultAirbyteMessageBufferedWriterFactory();
  }

  @AfterEach
  void tearDown() throws IOException {
    // The log file needs to be present and empty
    final Path logFile = logJobRoot.resolve(LogClientSingleton.LOG_FILENAME);
    if (Files.exists(logFile)) {
      Files.delete(logFile);
    }
    Files.createFile(logFile);
  }

  @SuppressWarnings("BusyWait")
  @Test
  void testSuccessfulLifecycle() throws Exception {
    final AirbyteDestination destination =
        new DefaultAirbyteDestination(integrationLauncher, streamFactory, messageWriterFactory, protocolSerializer);
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

    destination.notifyEndOfInput();

    verify(outputStream).close();

    destination.close();

    Assertions.assertEquals(MESSAGES, messages);

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).exitValue();
  }

  @Test
  void testTaggedLogs() throws Exception {

    final AirbyteDestination destination =
        new DefaultAirbyteDestination(integrationLauncher, streamFactory, messageWriterFactory, protocolSerializer);
    destination.start(DESTINATION_CONFIG, jobRoot);

    final AirbyteMessage recordMessage = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "blue");
    destination.accept(recordMessage);

    final List<AirbyteMessage> messages = Lists.newArrayList();

    messages.add(destination.attemptRead().get());
    messages.add(destination.attemptRead().get());

    when(process.isAlive()).thenReturn(false);

    destination.notifyEndOfInput();

    destination.close();

    final Path logPath = logJobRoot.resolve(LogClientSingleton.LOG_FILENAME);
    final Stream<String> logs = IOs.readFile(logPath).lines();

    logs.forEach(line -> {
      org.assertj.core.api.Assertions.assertThat(line)
          .startsWith(Color.YELLOW_BACKGROUND.getCode() + "destination" + RESET);
    });
  }

  @Test
  void testCloseNotifiesLifecycle() throws Exception {
    final AirbyteDestination destination = new DefaultAirbyteDestination(integrationLauncher);
    destination.start(DESTINATION_CONFIG, jobRoot);

    verify(outputStream, never()).close();

    when(process.isAlive()).thenReturn(false);
    destination.close();
    verify(outputStream).close();
  }

  @Test
  void testNonzeroExitCodeThrowsException() throws Exception {
    final AirbyteDestination destination = new DefaultAirbyteDestination(integrationLauncher);
    destination.start(DESTINATION_CONFIG, jobRoot);

    when(process.isAlive()).thenReturn(false);
    when(process.exitValue()).thenReturn(1);
    Assertions.assertThrows(WorkerException.class, destination::close);
  }

  @Test
  void testIgnoredExitCodes() throws Exception {
    final AirbyteDestination destination = new DefaultAirbyteDestination(integrationLauncher);
    destination.start(DESTINATION_CONFIG, jobRoot);
    when(process.isAlive()).thenReturn(false);

    DefaultAirbyteDestination.IGNORED_EXIT_CODES.forEach(exitCode -> {
      when(process.exitValue()).thenReturn(exitCode);
      Assertions.assertDoesNotThrow(destination::close);
    });
  }

  @Test
  void testGetExitValue() throws Exception {
    final AirbyteDestination destination = new DefaultAirbyteDestination(integrationLauncher);
    destination.start(DESTINATION_CONFIG, jobRoot);

    when(process.isAlive()).thenReturn(false);
    when(process.exitValue()).thenReturn(2);

    assertEquals(2, destination.getExitValue());
    // call a second time to verify that exit value is cached
    assertEquals(2, destination.getExitValue());
    verify(process, times(1)).exitValue();
  }

}
