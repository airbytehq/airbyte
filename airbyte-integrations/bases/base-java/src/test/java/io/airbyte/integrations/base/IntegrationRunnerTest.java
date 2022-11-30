/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.catchThrowable;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.apache.commons.lang3.ThreadUtils;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InOrder;
import org.mockito.Mockito;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class IntegrationRunnerTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(IntegrationRunnerTest.class);

  private static final String CONFIG_FILE_NAME = "config.json";
  private static final String CONFIGURED_CATALOG_FILE_NAME = "configured_catalog.json";
  private static final String STATE_FILE_NAME = "state.json";

  private static final String[] ARGS = new String[] {"args"};

  private static final String CONFIG_STRING = "{ \"username\": \"airbyte\" }";
  private static final JsonNode CONFIG = Jsons.deserialize(CONFIG_STRING);
  private static final String STREAM_NAME = "users";
  private static final Long EMITTED_AT = Instant.now().toEpochMilli();
  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");

  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(Lists.newArrayList(new AirbyteStream().withName(STREAM_NAME)));
  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = CatalogHelpers.toDefaultConfiguredCatalog(CATALOG);
  private static final JsonNode STATE = Jsons.jsonNode(ImmutableMap.of("checkpoint", "05/08/1945"));

  private IntegrationCliParser cliParser;
  private Consumer<AirbyteMessage> stdoutConsumer;
  private Destination destination;
  private Source source;
  private Path configPath;
  private Path configuredCatalogPath;
  private Path statePath;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws IOException {
    cliParser = mock(IntegrationCliParser.class);
    stdoutConsumer = Mockito.mock(Consumer.class);
    destination = mock(Destination.class);
    source = mock(Source.class);
    final Path configDir = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "test");

    configPath = IOs.writeFile(configDir, CONFIG_FILE_NAME, CONFIG_STRING);
    configuredCatalogPath = IOs.writeFile(configDir, CONFIGURED_CATALOG_FILE_NAME, Jsons.serialize(CONFIGURED_CATALOG));
    statePath = IOs.writeFile(configDir, STATE_FILE_NAME, Jsons.serialize(STATE));

    final String testName = Thread.currentThread().getName();
    ThreadUtils.getAllThreads()
        .stream()
        .filter(runningThread -> !runningThread.isDaemon())
        .forEach(runningThread -> runningThread.setName(testName));
  }

  @Test
  void testSpecSource() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.spec();
    final ConnectorSpecification output = new ConnectorSpecification().withDocumentationUrl(new URI("https://docs.airbyte.io/"));

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(source.spec()).thenReturn(output);

    new IntegrationRunner(cliParser, stdoutConsumer, null, source).run(ARGS);

    verify(source).spec();
    verify(stdoutConsumer).accept(new AirbyteMessage().withType(Type.SPEC).withSpec(output));
  }

  @Test
  void testSpecDestination() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.spec();
    final ConnectorSpecification output = new ConnectorSpecification().withDocumentationUrl(new URI("https://docs.airbyte.io/"));

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(destination.spec()).thenReturn(output);

    new IntegrationRunner(cliParser, stdoutConsumer, destination, null).run(ARGS);

    verify(destination).spec();
    verify(stdoutConsumer).accept(new AirbyteMessage().withType(Type.SPEC).withSpec(output));
  }

  @Test
  void testCheckSource() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.check(configPath);
    final AirbyteConnectionStatus output = new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage("it failed");

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(source.check(CONFIG)).thenReturn(output);

    final ConnectorSpecification expectedConnSpec = mock(ConnectorSpecification.class);
    when(source.spec()).thenReturn(expectedConnSpec);
    when(expectedConnSpec.getConnectionSpecification()).thenReturn(CONFIG);
    final JsonSchemaValidator jsonSchemaValidator = mock(JsonSchemaValidator.class);
    new IntegrationRunner(cliParser, stdoutConsumer, null, source, jsonSchemaValidator).run(ARGS);

    verify(source).check(CONFIG);
    verify(stdoutConsumer).accept(new AirbyteMessage().withType(Type.CONNECTION_STATUS).withConnectionStatus(output));
    verify(jsonSchemaValidator).validate(any(), any());
  }

  @Test
  void testCheckDestination() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.check(configPath);
    final AirbyteConnectionStatus output = new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage("it failed");

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(destination.check(CONFIG)).thenReturn(output);

    final ConnectorSpecification expectedConnSpec = mock(ConnectorSpecification.class);
    when(destination.spec()).thenReturn(expectedConnSpec);
    when(expectedConnSpec.getConnectionSpecification()).thenReturn(CONFIG);

    final JsonSchemaValidator jsonSchemaValidator = mock(JsonSchemaValidator.class);

    new IntegrationRunner(cliParser, stdoutConsumer, destination, null, jsonSchemaValidator).run(ARGS);

    verify(destination).check(CONFIG);
    verify(stdoutConsumer).accept(new AirbyteMessage().withType(Type.CONNECTION_STATUS).withConnectionStatus(output));
    verify(jsonSchemaValidator).validate(any(), any());
  }

  @Test
  void testDiscover() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.discover(configPath);
    final AirbyteCatalog output = new AirbyteCatalog()
        .withStreams(Lists.newArrayList(new AirbyteStream().withName("oceans")));

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(source.discover(CONFIG)).thenReturn(output);

    final ConnectorSpecification expectedConnSpec = mock(ConnectorSpecification.class);
    when(source.spec()).thenReturn(expectedConnSpec);
    when(expectedConnSpec.getConnectionSpecification()).thenReturn(CONFIG);

    final JsonSchemaValidator jsonSchemaValidator = mock(JsonSchemaValidator.class);
    new IntegrationRunner(cliParser, stdoutConsumer, null, source, jsonSchemaValidator).run(ARGS);

    verify(source).discover(CONFIG);
    verify(stdoutConsumer).accept(new AirbyteMessage().withType(Type.CATALOG).withCatalog(output));
    verify(jsonSchemaValidator).validate(any(), any());
  }

  @Test
  void testRead() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.read(configPath, configuredCatalogPath,
        statePath);
    final AirbyteMessage message1 = new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withData(Jsons.jsonNode(ImmutableMap.of("names", "byron"))));
    final AirbyteMessage message2 = new AirbyteMessage().withType(Type.RECORD).withRecord(new AirbyteRecordMessage()
        .withData(Jsons.jsonNode(ImmutableMap.of("names", "reginald"))));

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(source.read(CONFIG, CONFIGURED_CATALOG, STATE))
        .thenReturn(AutoCloseableIterators.fromIterator(MoreIterators.of(message1, message2)));

    final ConnectorSpecification expectedConnSpec = mock(ConnectorSpecification.class);
    when(source.spec()).thenReturn(expectedConnSpec);
    when(expectedConnSpec.getConnectionSpecification()).thenReturn(CONFIG);

    final JsonSchemaValidator jsonSchemaValidator = mock(JsonSchemaValidator.class);
    new IntegrationRunner(cliParser, stdoutConsumer, null, source, jsonSchemaValidator).run(ARGS);

    verify(source).read(CONFIG, CONFIGURED_CATALOG, STATE);
    verify(stdoutConsumer).accept(message1);
    verify(stdoutConsumer).accept(message2);
    verify(jsonSchemaValidator).validate(any(), any());
  }

  @Test
  void testReadException() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.read(configPath, configuredCatalogPath,
        statePath);
    final ConfigErrorException configErrorException = new ConfigErrorException("Invalid configuration");

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(source.read(CONFIG, CONFIGURED_CATALOG, STATE)).thenThrow(configErrorException);

    final ConnectorSpecification expectedConnSpec = mock(ConnectorSpecification.class);
    when(source.spec()).thenReturn(expectedConnSpec);
    when(expectedConnSpec.getConnectionSpecification()).thenReturn(CONFIG);

    final JsonSchemaValidator jsonSchemaValidator = mock(JsonSchemaValidator.class);
    final Throwable throwable = catchThrowable(() -> new IntegrationRunner(cliParser, stdoutConsumer, null, source, jsonSchemaValidator).run(ARGS));

    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    verify(source).read(CONFIG, CONFIGURED_CATALOG, STATE);
  }

  @Test
  void testCheckNestedException() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.check(configPath);
    final AirbyteConnectionStatus output = new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage("Invalid configuration");
    final ConfigErrorException configErrorException = new ConfigErrorException("Invalid configuration");
    final RuntimeException runtimeException = new RuntimeException(new RuntimeException(configErrorException));

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(source.check(CONFIG)).thenThrow(runtimeException);

    final ConnectorSpecification expectedConnSpec = mock(ConnectorSpecification.class);
    when(source.spec()).thenReturn(expectedConnSpec);
    when(expectedConnSpec.getConnectionSpecification()).thenReturn(CONFIG);
    final JsonSchemaValidator jsonSchemaValidator = mock(JsonSchemaValidator.class);
    new IntegrationRunner(cliParser, stdoutConsumer, null, source, jsonSchemaValidator).run(ARGS);

    verify(source).check(CONFIG);
    verify(stdoutConsumer).accept(new AirbyteMessage().withType(Type.CONNECTION_STATUS).withConnectionStatus(output));
    verify(jsonSchemaValidator).validate(any(), any());
  }

  @Test
  void testCheckRuntimeException() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.check(configPath);
    final AirbyteConnectionStatus output = new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage("Runtime Error");
    final RuntimeException runtimeException = new RuntimeException("Runtime Error");

    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(source.check(CONFIG)).thenThrow(runtimeException);

    final ConnectorSpecification expectedConnSpec = mock(ConnectorSpecification.class);
    when(source.spec()).thenReturn(expectedConnSpec);
    when(expectedConnSpec.getConnectionSpecification()).thenReturn(CONFIG);
    final JsonSchemaValidator jsonSchemaValidator = mock(JsonSchemaValidator.class);
    new IntegrationRunner(cliParser, stdoutConsumer, null, source, jsonSchemaValidator).run(ARGS);

    verify(source).check(CONFIG);
    verify(stdoutConsumer).accept(new AirbyteMessage().withType(Type.CONNECTION_STATUS).withConnectionStatus(output));
    verify(jsonSchemaValidator).validate(any(), any());
  }

  @Test
  void testWrite() throws Exception {
    final IntegrationConfig intConfig = IntegrationConfig.write(configPath, configuredCatalogPath);
    final AirbyteMessageConsumer airbyteMessageConsumerMock = mock(AirbyteMessageConsumer.class);
    when(cliParser.parse(ARGS)).thenReturn(intConfig);
    when(destination.getConsumer(CONFIG, CONFIGURED_CATALOG, stdoutConsumer)).thenReturn(airbyteMessageConsumerMock);

    final ConnectorSpecification expectedConnSpec = mock(ConnectorSpecification.class);
    when(destination.spec()).thenReturn(expectedConnSpec);
    when(expectedConnSpec.getConnectionSpecification()).thenReturn(CONFIG);

    final JsonSchemaValidator jsonSchemaValidator = mock(JsonSchemaValidator.class);

    final IntegrationRunner runner = spy(new IntegrationRunner(cliParser, stdoutConsumer, destination, null, jsonSchemaValidator));
    runner.run(ARGS);

    verify(destination).getConsumer(CONFIG, CONFIGURED_CATALOG, stdoutConsumer);
    verify(jsonSchemaValidator).validate(any(), any());
  }

  @Test
  void testDestinationConsumerLifecycleSuccess() throws Exception {
    final AirbyteMessage message1 = new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withData(Jsons.deserialize("{ \"color\": \"blue\" }"))
            .withStream(STREAM_NAME)
            .withEmittedAt(EMITTED_AT));
    final AirbyteMessage message2 = new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withData(Jsons.deserialize("{ \"color\": \"yellow\" }"))
            .withStream(STREAM_NAME)
            .withEmittedAt(EMITTED_AT));
    final AirbyteMessage stateMessage = new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.deserialize("{ \"checkpoint\": \"1\" }")));
    System.setIn(new ByteArrayInputStream((Jsons.serialize(message1) + "\n"
        + Jsons.serialize(message2) + "\n"
        + Jsons.serialize(stateMessage)).getBytes(StandardCharsets.UTF_8)));

    try (final AirbyteMessageConsumer airbyteMessageConsumerMock = mock(AirbyteMessageConsumer.class)) {
      IntegrationRunner.consumeWriteStream(airbyteMessageConsumerMock);
      final InOrder inOrder = inOrder(airbyteMessageConsumerMock);
      inOrder.verify(airbyteMessageConsumerMock).accept(message1);
      inOrder.verify(airbyteMessageConsumerMock).accept(message2);
      inOrder.verify(airbyteMessageConsumerMock).accept(stateMessage);
    }
  }

  @Test
  void testDestinationConsumerLifecycleFailure() throws Exception {
    final AirbyteMessage message1 = new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withData(Jsons.deserialize("{ \"color\": \"blue\" }"))
            .withStream(STREAM_NAME)
            .withEmittedAt(EMITTED_AT));
    final AirbyteMessage message2 = new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withData(Jsons.deserialize("{ \"color\": \"yellow\" }"))
            .withStream(STREAM_NAME)
            .withEmittedAt(EMITTED_AT));
    System.setIn(new ByteArrayInputStream((Jsons.serialize(message1) + "\n" + Jsons.serialize(message2)).getBytes(StandardCharsets.UTF_8)));

    try (final AirbyteMessageConsumer airbyteMessageConsumerMock = mock(AirbyteMessageConsumer.class)) {
      doThrow(new IOException("error")).when(airbyteMessageConsumerMock).accept(message1);
      assertThrows(IOException.class, () -> IntegrationRunner.consumeWriteStream(airbyteMessageConsumerMock));
      final InOrder inOrder = inOrder(airbyteMessageConsumerMock);
      inOrder.verify(airbyteMessageConsumerMock).accept(message1);
      inOrder.verifyNoMoreInteractions();
    }
  }

  @Test
  void testInterruptOrphanThreadFailure() {
    final String testName = Thread.currentThread().getName();
    final List<Exception> caughtExceptions = new ArrayList<>();
    startSleepingThread(caughtExceptions, false);
    assertThrows(IOException.class, () -> IntegrationRunner.watchForOrphanThreads(
        () -> {
          throw new IOException("random error");
        },
        Assertions::fail,
        3, TimeUnit.SECONDS,
        10, TimeUnit.SECONDS));
    try {
      TimeUnit.SECONDS.sleep(15);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
    final List<Thread> runningThreads = ThreadUtils.getAllThreads().stream()
        .filter(runningThread -> !runningThread.isDaemon() && !runningThread.getName().equals(testName))
        .collect(Collectors.toList());
    // all threads should be interrupted
    assertEquals(List.of(), runningThreads);
    assertEquals(1, caughtExceptions.size());
  }

  @Test
  void testNoInterruptOrphanThreadFailure() {
    final String testName = Thread.currentThread().getName();
    final List<Exception> caughtExceptions = new ArrayList<>();
    final AtomicBoolean exitCalled = new AtomicBoolean(false);
    startSleepingThread(caughtExceptions, true);
    assertThrows(IOException.class, () -> IntegrationRunner.watchForOrphanThreads(
        () -> {
          throw new IOException("random error");
        },
        () -> exitCalled.set(true),
        3, TimeUnit.SECONDS,
        10, TimeUnit.SECONDS));
    try {
      TimeUnit.SECONDS.sleep(15);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
    final List<Thread> runningThreads = ThreadUtils.getAllThreads().stream()
        .filter(runningThread -> !runningThread.isDaemon() && !runningThread.getName().equals(testName))
        .collect(Collectors.toList());
    // a thread that refuses to be interrupted should remain
    assertEquals(1, runningThreads.size());
    assertEquals(1, caughtExceptions.size());
    assertTrue(exitCalled.get());
  }

  private void startSleepingThread(final List<Exception> caughtExceptions, final boolean ignoreInterrupt) {
    final ExecutorService executorService = Executors.newFixedThreadPool(1);
    executorService.submit(() -> {
      for (int tries = 0; tries < 3; tries++) {
        try {
          TimeUnit.MINUTES.sleep(5);
        } catch (final Exception e) {
          LOGGER.info("Caught Exception", e);
          caughtExceptions.add(e);
          if (!ignoreInterrupt) {
            executorService.shutdownNow();
            break;
          }
        }
      }
    });
  }

  @Test
  void testParseConnectorImage() {
    assertEquals("unknown", IntegrationRunner.parseConnectorVersion(null));
    assertEquals("unknown", IntegrationRunner.parseConnectorVersion(""));
    assertEquals("1.0.1-alpha", IntegrationRunner.parseConnectorVersion("airbyte/destination-test:1.0.1-alpha"));
    assertEquals("dev", IntegrationRunner.parseConnectorVersion("airbyte/destination-test:dev"));
    assertEquals("1.0.1-alpha", IntegrationRunner.parseConnectorVersion("destination-test:1.0.1-alpha"));
    assertEquals("1.0.1-alpha", IntegrationRunner.parseConnectorVersion(":1.0.1-alpha"));
  }

  @Test
  void testConsumptionOfInvalidStateMessage() {
    final String invalidStateMessage = """
                                       {
                                         "type" : "STATE",
                                         "state" : {
                                           "type": "NOT_RECOGNIZED",
                                           "global": {
                                             "streamStates": {
                                               "foo" : "bar"
                                             }
                                           }
                                         }
                                       }
                                       """;

    Assertions.assertThrows(IllegalStateException.class, () -> {
      try (final AirbyteMessageConsumer consumer = mock(AirbyteMessageConsumer.class)) {
        IntegrationRunner.consumeMessage(consumer, invalidStateMessage);
      }
    });
  }

  @Test
  void testConsumptionOfInvalidNonStateMessage() {
    final String invalidNonStateMessage = """
                                          {
                                            "type" : "NOT_RECOGNIZED",
                                            "record" : {
                                              "namespace": "namespace",
                                              "stream": "stream",
                                              "emittedAt": 123456789
                                            }
                                          }
                                          """;

    Assertions.assertDoesNotThrow(() -> {
      try (final AirbyteMessageConsumer consumer = mock(AirbyteMessageConsumer.class)) {
        IntegrationRunner.consumeMessage(consumer, invalidNonStateMessage);
        verify(consumer, times(0)).accept(any(AirbyteMessage.class));
      }
    });
  }

}
