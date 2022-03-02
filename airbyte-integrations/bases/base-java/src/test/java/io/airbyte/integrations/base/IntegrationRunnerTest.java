/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
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
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.apache.commons.lang3.ThreadUtils;
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
  private static final NoExitSecurityManager noExitSecurityManager = new NoExitSecurityManager();

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
    noExitSecurityManager.setExitStatus(false);
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
        + Jsons.serialize(stateMessage)).getBytes()));

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
    System.setIn(new ByteArrayInputStream((Jsons.serialize(message1) + "\n" + Jsons.serialize(message2)).getBytes()));

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
    System.setIn(new ByteArrayInputStream("{}\n{}".getBytes()));
    final String testName = Thread.currentThread().getName();
    noExitSecurityManager.setExitStatus(false);
    try (final MultiThreadTestConsumer airbyteMessageConsumerMock = new MultiThreadTestConsumer(false)) {
      assertThrows(IOException.class, () -> IntegrationRunner.consumeWriteStream(airbyteMessageConsumerMock,
          3, TimeUnit.SECONDS,
          10, TimeUnit.SECONDS));
      try {
        TimeUnit.SECONDS.sleep(10);
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
      final List<Thread> runningThreads = ThreadUtils.getAllThreads().stream()
          .filter(runningThread -> !runningThread.isDaemon() && !runningThread.getName().equals(testName))
          .collect(Collectors.toList());
      // all threads should be interrupted
      assertEquals(List.of(), runningThreads);
      assertTrue(airbyteMessageConsumerMock.hasCaughtExceptions());
      // We don't need to force a system.exit
      assertFalse(noExitSecurityManager.checkExitStatus());
    }
  }

  @Test
  void testNoInterruptOrphanThreadFailure() {
    System.setIn(new ByteArrayInputStream("{}\n{}".getBytes()));
    final String testName = Thread.currentThread().getName();
    noExitSecurityManager.setExitStatus(false);
    try (final MultiThreadTestConsumer airbyteMessageConsumerMock = new MultiThreadTestConsumer(true)) {
      assertThrows(IOException.class, () -> IntegrationRunner.consumeWriteStream(airbyteMessageConsumerMock,
          3, TimeUnit.SECONDS,
          10, TimeUnit.SECONDS));
      try {
        TimeUnit.SECONDS.sleep(10);
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
      final List<Thread> runningThreads = ThreadUtils.getAllThreads().stream()
          .filter(runningThread -> !runningThread.isDaemon() && !runningThread.getName().equals(testName))
          .collect(Collectors.toList());
      // A remaining thread is still alive as it refuses to be interrupted
      assertEquals(1, runningThreads.size());
      assertTrue(airbyteMessageConsumerMock.hasCaughtExceptions());
      // We need to force a system.exit
      assertTrue(noExitSecurityManager.checkExitStatus());
    }
  }

  private static class MultiThreadTestConsumer implements AirbyteMessageConsumer, Runnable {

    final private ExecutorService executorService = Executors.newFixedThreadPool(1);
    private final boolean ignoreInterrupt;
    private boolean interruptException = false;

    public MultiThreadTestConsumer(final boolean ignoreInterrupt) {
      this.ignoreInterrupt = ignoreInterrupt;
    }

    @Override
    public void start() {
      executorService.submit(this);
    }

    @Override
    public void accept(AirbyteMessage message) throws Exception {
      throw new IOException("Some random exceptions");
    }

    @Override
    public void run() {
      try {
        TimeUnit.MINUTES.sleep(5);
      } catch (Exception e) {
        LOGGER.info("Caught Exception", e);
        interruptException = true;
        if (ignoreInterrupt) {
          // for test purposes, we simulate a consumer that refuses to be interrupted...
          run();
        } else {
          close();
        }
      }
    }

    @Override
    public void close() {
      executorService.shutdownNow();
    }

    public boolean hasCaughtExceptions() {
      return interruptException;
    }

  }

  private static class NoExitSecurityManager extends SecurityManager {

    private boolean triedToExit = false;

    public NoExitSecurityManager() {
      System.setSecurityManager(this);
    }

    @Override
    public void checkExit(int status) {
      LOGGER.info("Trying to exit");
      triedToExit = true;
      super.checkExit(status);
      throw new SecurityException("Not allowed in this test.");
    }

    public boolean checkExitStatus() {
      return triedToExit;
    }

    public void setExitStatus(boolean triedToExit) {
      this.triedToExit = triedToExit;
    }

  }

}
