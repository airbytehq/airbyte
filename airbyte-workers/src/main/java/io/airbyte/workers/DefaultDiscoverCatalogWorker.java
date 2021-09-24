/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.protocols.airbyte.AirbyteStreamFactory;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteStreamFactory;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultDiscoverCatalogWorker implements DiscoverCatalogWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultDiscoverCatalogWorker.class);

  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;

  private volatile Process process;

  public DefaultDiscoverCatalogWorker(final IntegrationLauncher integrationLauncher, final AirbyteStreamFactory streamFactory) {
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
  }

  public DefaultDiscoverCatalogWorker(final IntegrationLauncher integrationLauncher) {
    this(integrationLauncher, new DefaultAirbyteStreamFactory());
  }

  @Override
  public AirbyteCatalog run(final StandardDiscoverCatalogInput discoverSchemaInput, final Path jobRoot) throws WorkerException {
    try {
      process = integrationLauncher.discover(
          jobRoot,
          WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
          Jsons.serialize(discoverSchemaInput.getConnectionConfiguration()));

      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      Optional<AirbyteCatalog> catalog;
      try (InputStream stdout = process.getInputStream()) {
        catalog = streamFactory.create(IOs.newBufferedReader(stdout))
            .filter(message -> message.getType() == Type.CATALOG)
            .map(AirbyteMessage::getCatalog)
            .findFirst();

        WorkerUtils.gentleClose(process, 30, TimeUnit.MINUTES);
      }

      int exitCode = process.exitValue();
      if (exitCode == 0) {
        if (catalog.isEmpty()) {
          throw new WorkerException("Integration failed to output a catalog struct.");
        }

        return catalog.get();
      } else {
        throw new WorkerException(String.format("Discover job subprocess finished with exit code %s", exitCode));
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
