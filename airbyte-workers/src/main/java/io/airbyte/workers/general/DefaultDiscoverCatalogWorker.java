/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultDiscoverCatalogWorker implements DiscoverCatalogWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultDiscoverCatalogWorker.class);

  private final ConfigRepository configRepository;

  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;

  private volatile Process process;

  public DefaultDiscoverCatalogWorker(final ConfigRepository configRepository,
                                      final IntegrationLauncher integrationLauncher,
                                      final AirbyteStreamFactory streamFactory) {
    this.configRepository = configRepository;
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
  }

  public DefaultDiscoverCatalogWorker(final ConfigRepository configRepository,
                                      final IntegrationLauncher integrationLauncher) {
    this(configRepository, integrationLauncher, new DefaultAirbyteStreamFactory());
  }

  @Override
  public ConnectorJobOutput run(final StandardDiscoverCatalogInput discoverSchemaInput, final Path jobRoot) throws WorkerException {
    try {
      process = integrationLauncher.discover(
          jobRoot,
          WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
          Jsons.serialize(discoverSchemaInput.getConnectionConfiguration()));

      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      final Map<Type, List<AirbyteMessage>> messagesByType;

      try (final InputStream stdout = process.getInputStream()) {
        messagesByType = streamFactory.create(IOs.newBufferedReader(stdout))
            .collect(Collectors.groupingBy(AirbyteMessage::getType));

        WorkerUtils.gentleClose(process, 30, TimeUnit.MINUTES);
      }

      final Optional<AirbyteCatalog> catalog = messagesByType
          .getOrDefault(Type.CATALOG, new ArrayList<>()).stream()
          .map(AirbyteMessage::getCatalog)
          .findFirst();

      final int exitCode = process.exitValue();
      if (exitCode == 0) {
        if (catalog.isEmpty()) {
          throw new WorkerException("Integration failed to output a catalog struct.");
        }

        final UUID catalogId =
            configRepository.writeActorCatalogFetchEvent(catalog.get(),
                // NOTE: sourceId is marked required in the OpenAPI config but the code generator doesn't enforce
                // it, so we check again here.
                discoverSchemaInput.getSourceId() == null ? null : UUID.fromString(discoverSchemaInput.getSourceId()),
                discoverSchemaInput.getConnectorVersion(),
                discoverSchemaInput.getConfigHash());
        return new ConnectorJobOutput().withOutputType(OutputType.DISCOVER_CATALOG_ID).withDiscoverCatalogId(catalogId);
      } else {
        return WorkerUtils.getJobFailureOutputOrThrow(
            OutputType.DISCOVER_CATALOG_ID,
            messagesByType,
            String.format("Discover job subprocess finished with exit code %s", exitCode));
      }
    } catch (final WorkerException e) {
      throw e;
    } catch (final Exception e) {
      throw new WorkerException("Error while discovering schema", e);
    }
  }

  @Override
  public void cancel() {
    WorkerUtils.cancelProcess(process);
  }

}
