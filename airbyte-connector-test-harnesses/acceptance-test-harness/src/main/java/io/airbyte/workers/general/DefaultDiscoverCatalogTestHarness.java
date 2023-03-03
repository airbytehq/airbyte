/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.model.generated.DiscoverCatalogResult;
import io.airbyte.api.client.model.generated.SourceDiscoverSchemaWriteRequestBody;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteControlConnectorConfigMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.workers.TestHarnessUtils;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.exception.TestHarnessException;
import io.airbyte.workers.helper.CatalogClientConverters;
import io.airbyte.workers.helper.ConnectorConfigUpdater;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultDiscoverCatalogTestHarness implements DiscoverCatalogTestHarness {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultDiscoverCatalogTestHarness.class);
  private static final String WRITE_DISCOVER_CATALOG_LOGS_TAG = "call to write discover schema result";

  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;
  private final ConnectorConfigUpdater connectorConfigUpdater;
  private final AirbyteApiClient airbyteApiClient;
  private volatile Process process;

  public DefaultDiscoverCatalogTestHarness(final AirbyteApiClient airbyteApiClient,
                                           final IntegrationLauncher integrationLauncher,
                                           final ConnectorConfigUpdater connectorConfigUpdater,
                                           final AirbyteStreamFactory streamFactory) {
    this.airbyteApiClient = airbyteApiClient;
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
    this.connectorConfigUpdater = connectorConfigUpdater;
  }

  public DefaultDiscoverCatalogTestHarness(final AirbyteApiClient airbyteApiClient,
                                           final IntegrationLauncher integrationLauncher,
                                           final ConnectorConfigUpdater connectorConfigUpdater) {
    this(airbyteApiClient, integrationLauncher, connectorConfigUpdater, new DefaultAirbyteStreamFactory());
  }

  @Override
  public ConnectorJobOutput run(final StandardDiscoverCatalogInput discoverSchemaInput, final Path jobRoot) throws TestHarnessException {
    try {
      final JsonNode inputConfig = discoverSchemaInput.getConnectionConfiguration();
      process = integrationLauncher.discover(
          jobRoot,
          WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
          Jsons.serialize(inputConfig));

      final ConnectorJobOutput jobOutput = new ConnectorJobOutput()
          .withOutputType(OutputType.DISCOVER_CATALOG_ID);

      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      final Map<Type, List<AirbyteMessage>> messagesByType = TestHarnessUtils.getMessagesByType(process, streamFactory, 30);

      final Optional<AirbyteCatalog> catalog = messagesByType
          .getOrDefault(Type.CATALOG, new ArrayList<>()).stream()
          .map(AirbyteMessage::getCatalog)
          .findFirst();

      final Optional<AirbyteControlConnectorConfigMessage> optionalConfigMsg = TestHarnessUtils.getMostRecentConfigControlMessage(messagesByType);
      if (optionalConfigMsg.isPresent() && TestHarnessUtils.getDidControlMessageChangeConfig(inputConfig, optionalConfigMsg.get())) {
        connectorConfigUpdater.updateSource(
            UUID.fromString(discoverSchemaInput.getSourceId()),
            optionalConfigMsg.get().getConfig());
        jobOutput.setConnectorConfigurationUpdated(true);
      }

      final Optional<FailureReason> failureReason = TestHarnessUtils.getJobFailureReasonFromMessages(OutputType.DISCOVER_CATALOG_ID, messagesByType);
      failureReason.ifPresent(jobOutput::setFailureReason);

      final int exitCode = process.exitValue();
      if (exitCode != 0) {
        LOGGER.warn("Discover job subprocess finished with exit codee {}", exitCode);
      }

      if (catalog.isPresent()) {
        final DiscoverCatalogResult result =
            AirbyteApiClient.retryWithJitter(() -> airbyteApiClient.getSourceApi()
                .writeDiscoverCatalogResult(buildSourceDiscoverSchemaWriteRequestBody(discoverSchemaInput, catalog.get())),
                WRITE_DISCOVER_CATALOG_LOGS_TAG);
        jobOutput.setDiscoverCatalogId(result.getCatalogId());
      } else if (failureReason.isEmpty()) {
        TestHarnessUtils.throwWorkerException("Integration failed to output a catalog struct and did not output a failure reason", process);
      }
      return jobOutput;
    } catch (final TestHarnessException e) {
      throw e;
    } catch (final Exception e) {
      throw new TestHarnessException("Error while discovering schema", e);
    }
  }

  private SourceDiscoverSchemaWriteRequestBody buildSourceDiscoverSchemaWriteRequestBody(final StandardDiscoverCatalogInput discoverSchemaInput,
                                                                                         final AirbyteCatalog catalog) {
    return new SourceDiscoverSchemaWriteRequestBody().catalog(
        CatalogClientConverters.toAirbyteCatalogClientApi(catalog)).sourceId(
            // NOTE: sourceId is marked required in the OpenAPI config but the code generator doesn't enforce
            // it, so we check again here.
            discoverSchemaInput.getSourceId() == null ? null : UUID.fromString(discoverSchemaInput.getSourceId()))
        .connectorVersion(
            discoverSchemaInput.getConnectorVersion())
        .configurationHash(
            discoverSchemaInput.getConfigHash());
  }

  @Override
  public void cancel() {
    TestHarnessUtils.cancelProcess(process);
  }

}
