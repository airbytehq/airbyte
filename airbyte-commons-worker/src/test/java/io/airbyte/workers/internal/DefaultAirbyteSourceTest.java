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
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.LoggingHelper.Color;
import io.airbyte.commons.protocol.DefaultProtocolSerializer;
import io.airbyte.commons.protocol.ProtocolSerializer;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.State;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class DefaultAirbyteSourceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultAirbyteSourceTest.class);
  private static final String NAMESPACE = "unused";
  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";

  private static final JsonNode STATE = Jsons.jsonNode(ImmutableMap.of("checkpoint", "the future."));
  private static final JsonNode CONFIG = Jsons.jsonNode(Map.of(
      "apiKey", "123",
      "region", "us-east"));
  private static final ConfiguredAirbyteCatalog CATALOG = CatalogHelpers.createConfiguredAirbyteCatalog(
      "hudi:latest",
      NAMESPACE,
      Field.of(FIELD_NAME, JsonSchemaType.STRING));

  private static final WorkerSourceConfig SOURCE_CONFIG = new WorkerSourceConfig()
      .withState(new State().withState(STATE))
      .withSourceConnectionConfiguration(CONFIG)
      .withCatalog(CATALOG);

  private static final List<AirbyteMessage> MESSAGES = Lists.newArrayList(
      AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "blue"),
      AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "yellow"));

  private static Path logJobRoot;

  private static final FeatureFlags featureFlags = new EnvVariableFeatureFlags();

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
  private HeartbeatMonitor heartbeatMonitor;
  private final ProtocolSerializer protocolSerializer = new DefaultProtocolSerializer();

  @BeforeEach
  void setup() throws IOException, WorkerException {
    jobRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "test");

    integrationLauncher = mock(IntegrationLauncher.class, RETURNS_DEEP_STUBS);
    process = mock(Process.class, RETURNS_DEEP_STUBS);
    heartbeatMonitor = mock(HeartbeatMonitor.class);
    final InputStream inputStream = mock(InputStream.class);
    when(integrationLauncher.read(
        jobRoot,
        WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
        Jsons.serialize(CONFIG),
        WorkerConstants.SOURCE_CATALOG_JSON_FILENAME,
        Jsons.serialize(CATALOG),
        WorkerConstants.INPUT_STATE_JSON_FILENAME,
        Jsons.serialize(STATE))).thenReturn(process);
    when(process.isAlive()).thenReturn(true);
    when(process.getInputStream()).thenReturn(inputStream);
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream("qwer".getBytes(StandardCharsets.UTF_8)));

    streamFactory = noop -> MESSAGES.stream();

    LogClientSingleton.getInstance().setJobMdc(WorkerEnvironment.DOCKER, LogConfigs.EMPTY, logJobRoot);
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

  @SuppressWarnings({"OptionalGetWithoutIsPresent", "BusyWait"})
  @Test
  void testSuccessfulLifecycle() throws Exception {
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream("qwer".getBytes(StandardCharsets.UTF_8)));

    when(heartbeatMonitor.isBeating()).thenReturn(true).thenReturn(false);

    final AirbyteSource source = new DefaultAirbyteSource(integrationLauncher, streamFactory, heartbeatMonitor, protocolSerializer, featureFlags);
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

    assertEquals(MESSAGES, messages);

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).exitValue();
  }

  @Test
  void testTaggedLogs() throws Exception {

    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream(("rewq").getBytes(StandardCharsets.UTF_8)));

    when(heartbeatMonitor.isBeating()).thenReturn(true).thenReturn(false);

    final AirbyteSource source = new DefaultAirbyteSource(integrationLauncher, streamFactory,
        heartbeatMonitor, protocolSerializer, featureFlags);
    source.start(SOURCE_CONFIG, jobRoot);

    final List<AirbyteMessage> messages = Lists.newArrayList();

    messages.add(source.attemptRead().get());
    messages.add(source.attemptRead().get());

    when(process.isAlive()).thenReturn(false);

    source.close();

    final Path logPath = logJobRoot.resolve(LogClientSingleton.LOG_FILENAME);
    final Stream<String> logs = IOs.readFile(logPath).lines();

    logs
        .filter(line -> !line.contains("EnvConfigs(getEnvOrDefault)"))
        .forEach(line -> {
          org.assertj.core.api.Assertions.assertThat(line)
              .startsWith(Color.BLUE_BACKGROUND.getCode() + "source" + RESET);
        });
  }

  @Test
  void testNonzeroExitCodeThrows() throws Exception {
    final AirbyteSource tap = new DefaultAirbyteSource(integrationLauncher, streamFactory, heartbeatMonitor, protocolSerializer, featureFlags);
    tap.start(SOURCE_CONFIG, jobRoot);

    when(process.exitValue()).thenReturn(1);

    Assertions.assertThrows(WorkerException.class, tap::close);
  }

  @Test
  void testIgnoredExitCodes() throws Exception {
    final AirbyteSource tap = new DefaultAirbyteSource(integrationLauncher, streamFactory, heartbeatMonitor, protocolSerializer, featureFlags);
    tap.start(SOURCE_CONFIG, jobRoot);
    when(process.isAlive()).thenReturn(false);

    DefaultAirbyteSource.IGNORED_EXIT_CODES.forEach(exitCode -> {
      when(process.exitValue()).thenReturn(exitCode);
      Assertions.assertDoesNotThrow(tap::close);
    });
  }

  @Test
  void testGetExitValue() throws Exception {
    final AirbyteSource source = new DefaultAirbyteSource(integrationLauncher, streamFactory, heartbeatMonitor, protocolSerializer, featureFlags);
    source.start(SOURCE_CONFIG, jobRoot);

    when(process.isAlive()).thenReturn(false);
    when(process.exitValue()).thenReturn(2);

    assertEquals(2, source.getExitValue());
    // call a second time to verify that exit value is cached
    assertEquals(2, source.getExitValue());
    verify(process, times(1)).exitValue();
  }

}
