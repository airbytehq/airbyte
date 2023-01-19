/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.Config;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.helper.ConnectorConfigUpdater;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.UUID;
import java.util.stream.Stream;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;

@SuppressWarnings("PMD.AvoidDuplicateLiterals")
class DefaultDiscoverCatalogWorkerTest {

  @Mock
  private ConfigRepository mConfigRepository;

  private static final JsonNode CREDENTIALS = Jsons.jsonNode(ImmutableMap.builder().put("apiKey", "123").build());

  private static final UUID SOURCE_ID = UUID.randomUUID();
  private static final StandardDiscoverCatalogInput INPUT =
      new StandardDiscoverCatalogInput().withConnectionConfiguration(CREDENTIALS).withSourceId(SOURCE_ID.toString());

  private static final Path TEST_ROOT = Path.of("/tmp/airbyte_tests");
  private static final String STREAM = "users";
  private static final String COLUMN_NAME = "name";
  private static final String COLUMN_AGE = "age";
  private static final AirbyteCatalog CATALOG = new AirbyteCatalog()
      .withStreams(Lists.newArrayList(CatalogHelpers.createAirbyteStream(
          STREAM,
          Field.of(COLUMN_NAME, JsonSchemaType.STRING),
          Field.of(COLUMN_AGE, JsonSchemaType.NUMBER))));

  private Path jobRoot;
  private IntegrationLauncher integrationLauncher;
  private Process process;
  private AirbyteStreamFactory validCatalogStreamFactory;
  private AirbyteStreamFactory emptyStreamFactory;
  private AirbyteStreamFactory traceStreamFactory;
  private AirbyteStreamFactory validCatalogWithTraceMessageStreamFactory;
  private AirbyteStreamFactory streamFactory;
  private ConnectorConfigUpdater connectorConfigUpdater;

  private UUID CATALOG_ID;

  @BeforeEach
  void setup() throws Exception {
    jobRoot = Files.createTempDirectory(Files.createDirectories(TEST_ROOT), "");
    integrationLauncher = mock(IntegrationLauncher.class, RETURNS_DEEP_STUBS);
    process = mock(Process.class);
    mConfigRepository = mock(ConfigRepository.class);
    connectorConfigUpdater = mock(ConnectorConfigUpdater.class);

    CATALOG_ID = UUID.randomUUID();
    when(mConfigRepository.writeActorCatalogFetchEvent(any(), any(), any(), any())).thenReturn(CATALOG_ID);

    when(integrationLauncher.discover(jobRoot, WorkerConstants.SOURCE_CONFIG_JSON_FILENAME, Jsons.serialize(CREDENTIALS))).thenReturn(process);
    final InputStream inputStream = mock(InputStream.class);
    when(process.getInputStream()).thenReturn(inputStream);
    when(process.getErrorStream()).thenReturn(new ByteArrayInputStream(new byte[0]));

    IOs.writeFile(jobRoot, WorkerConstants.SOURCE_CATALOG_JSON_FILENAME, MoreResources.readResource("airbyte_postgres_catalog.json"));
    final AirbyteMessage traceMessage = AirbyteMessageUtils.createErrorMessage("some error from the connector", 123.0);

    validCatalogStreamFactory = noop -> Lists.newArrayList(new AirbyteMessage().withType(Type.CATALOG).withCatalog(CATALOG)).stream();
    traceStreamFactory = noop -> Lists.newArrayList(traceMessage).stream();
    emptyStreamFactory = noop -> Stream.empty();

    validCatalogWithTraceMessageStreamFactory =
        noop -> Lists.newArrayList(new AirbyteMessage().withType(Type.CATALOG).withCatalog(CATALOG), traceMessage).stream();

  }

  @SuppressWarnings("BusyWait")
  @Test
  void testDiscoverSchema() throws Exception {
    final DefaultDiscoverCatalogWorker worker =
        new DefaultDiscoverCatalogWorker(mConfigRepository, integrationLauncher, connectorConfigUpdater, validCatalogStreamFactory);
    final ConnectorJobOutput output = worker.run(INPUT, jobRoot);

    assertNull(output.getFailureReason());
    assertEquals(OutputType.DISCOVER_CATALOG_ID, output.getOutputType());
    assertEquals(CATALOG_ID, output.getDiscoverCatalogId());
    assertFalse(output.getConnectorConfigurationUpdated());
    verify(mConfigRepository).writeActorCatalogFetchEvent(eq(CATALOG), eq(SOURCE_ID), any(), any());
    verifyNoInteractions(connectorConfigUpdater);

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).exitValue();
  }

  @SuppressWarnings("BusyWait")
  @Test
  void testDiscoverSchemaWithConfigUpdate() throws Exception {
    final Config connectorConfig1 = new Config().withAdditionalProperty("apiKey", "123");
    final Config connectorConfig2 = new Config().withAdditionalProperty("apiKey", "321");
    final AirbyteStreamFactory configMsgStreamFactory = noop -> Lists.newArrayList(
        AirbyteMessageUtils.createConfigControlMessage(connectorConfig1, 1D),
        AirbyteMessageUtils.createConfigControlMessage(connectorConfig2, 2D),
        new AirbyteMessage().withType(Type.CATALOG).withCatalog(CATALOG)).stream();

    final DefaultDiscoverCatalogWorker worker =
        new DefaultDiscoverCatalogWorker(mConfigRepository, integrationLauncher, connectorConfigUpdater, configMsgStreamFactory);
    final ConnectorJobOutput output = worker.run(INPUT, jobRoot);

    assertNull(output.getFailureReason());
    assertEquals(OutputType.DISCOVER_CATALOG_ID, output.getOutputType());
    assertEquals(CATALOG_ID, output.getDiscoverCatalogId());
    assertTrue(output.getConnectorConfigurationUpdated());
    verify(mConfigRepository).writeActorCatalogFetchEvent(eq(CATALOG), eq(SOURCE_ID), any(), any());
    verify(connectorConfigUpdater).updateSource(SOURCE_ID, connectorConfig2);

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).exitValue();
  }

  @Test
  void testDiscoverSchemaWithConfigUpdateNoChange() throws Exception {
    final Config noChangeConfig = new Config().withAdditionalProperty("apiKey", "123");
    final AirbyteStreamFactory noChangeConfigMsgStreamFactory = noop -> Lists.newArrayList(
        AirbyteMessageUtils.createConfigControlMessage(noChangeConfig, 1D),
        new AirbyteMessage().withType(Type.CATALOG).withCatalog(CATALOG)).stream();

    final DefaultDiscoverCatalogWorker worker =
        new DefaultDiscoverCatalogWorker(mConfigRepository, integrationLauncher, connectorConfigUpdater, noChangeConfigMsgStreamFactory);
    final ConnectorJobOutput output = worker.run(INPUT, jobRoot);

    assertNull(output.getFailureReason());
    assertEquals(OutputType.DISCOVER_CATALOG_ID, output.getOutputType());
    assertEquals(CATALOG_ID, output.getDiscoverCatalogId());
    assertFalse(output.getConnectorConfigurationUpdated());
    verify(mConfigRepository).writeActorCatalogFetchEvent(eq(CATALOG), eq(SOURCE_ID), any(), any());
    verifyNoInteractions(connectorConfigUpdater);

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).exitValue();
  }

  @SuppressWarnings("BusyWait")
  @Test
  void testDiscoverSchemaProcessFailWithNoCatalogNoTraceMessage() {
    final DefaultDiscoverCatalogWorker worker =
        new DefaultDiscoverCatalogWorker(mConfigRepository, integrationLauncher, connectorConfigUpdater, emptyStreamFactory);
    assertThrows(WorkerException.class, () -> worker.run(INPUT, jobRoot));

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).exitValue();
  }

  @SuppressWarnings("BusyWait")
  @Test
  void testDiscoverSchemaHasFailureReasonWithTraceMessage() throws Exception {

    final DefaultDiscoverCatalogWorker worker =
        new DefaultDiscoverCatalogWorker(mConfigRepository, integrationLauncher, connectorConfigUpdater, traceStreamFactory);
    final ConnectorJobOutput output = worker.run(INPUT, jobRoot);
    assertEquals(output.getOutputType(), OutputType.DISCOVER_CATALOG_ID);
    assertNull(output.getDiscoverCatalogId());
    final FailureReason failureReason = output.getFailureReason();
    assertEquals("some error from the connector", failureReason.getExternalMessage());

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).exitValue();
  }

  @Test
  void testDiscoverSchemaHasFailureReasonAndCatalogWithCatalogAndTraceMessage() throws Exception {

    final DefaultDiscoverCatalogWorker worker =
        new DefaultDiscoverCatalogWorker(mConfigRepository, integrationLauncher, connectorConfigUpdater, validCatalogWithTraceMessageStreamFactory);
    final ConnectorJobOutput output = worker.run(INPUT, jobRoot);
    assertEquals(output.getOutputType(), OutputType.DISCOVER_CATALOG_ID);
    assertNotNull(output.getDiscoverCatalogId());
    final FailureReason failureReason = output.getFailureReason();
    assertEquals("some error from the connector", failureReason.getExternalMessage());

    Assertions.assertTimeout(Duration.ofSeconds(5), () -> {
      while (process.getErrorStream().available() != 0) {
        Thread.sleep(50);
      }
    });

    verify(process).exitValue();
  }

  @Test
  void testDiscoverSchemaException() throws WorkerException {
    when(integrationLauncher.discover(jobRoot, WorkerConstants.SOURCE_CONFIG_JSON_FILENAME, Jsons.serialize(CREDENTIALS)))
        .thenThrow(new RuntimeException());

    final DefaultDiscoverCatalogWorker worker =
        new DefaultDiscoverCatalogWorker(mConfigRepository, integrationLauncher, connectorConfigUpdater, validCatalogStreamFactory);
    assertThrows(WorkerException.class, () -> worker.run(INPUT, jobRoot));
  }

  @Test
  void testCancel() throws WorkerException {
    final DefaultDiscoverCatalogWorker worker =
        new DefaultDiscoverCatalogWorker(mConfigRepository, integrationLauncher, connectorConfigUpdater, validCatalogStreamFactory);
    worker.run(INPUT, jobRoot);

    worker.cancel();

    verify(process).destroy();
  }

}
