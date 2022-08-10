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
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.workers.*;
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
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultDiscoverCatalogWorker implements DiscoverCatalogWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultDiscoverCatalogWorker.class);
  private static final int TEMPORAL_MESSAGE_LIMIT_MB = 1024 * 1024 * 4;

  private final WorkerConfigs workerConfigs;
  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;

  private volatile Process process;

  public DefaultDiscoverCatalogWorker(final WorkerConfigs workerConfigs,
                                      final IntegrationLauncher integrationLauncher,
                                      final AirbyteStreamFactory streamFactory) {
    this.workerConfigs = workerConfigs;
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
  }

  public DefaultDiscoverCatalogWorker(final WorkerConfigs workerConfigs, final IntegrationLauncher integrationLauncher) {
    this(workerConfigs, integrationLauncher, new DefaultAirbyteStreamFactory());
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

        WorkerUtils.gentleClose(workerConfigs, process, 30, TimeUnit.MINUTES);
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

        // This message is sent through temporal that utilizes GRPC as is set to limit messages to 4mb.
        // We fail fast here so users will not have to wait the 10 minutes before a timeout error occurs.
        if (catalog.get().toString().length() > TEMPORAL_MESSAGE_LIMIT_MB) {
          throw new WorkerException("Output a catalog struct bigger than 4mb. Larger than grpc max message limit.");
        }

        return new ConnectorJobOutput().withOutputType(OutputType.DISCOVER_CATALOG).withDiscoverCatalog(catalog.get());
      } else {
        return WorkerUtils.getJobFailureOutputOrThrow(
            OutputType.DISCOVER_CATALOG,
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
