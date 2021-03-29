/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.workers;

import com.fasterxml.jackson.databind.JsonNode;
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

    final JsonNode configDotJson = discoverSchemaInput.getConnectionConfiguration();
    IOs.writeFile(jobRoot, WorkerConstants.SOURCE_CONFIG_JSON_FILENAME, Jsons.serialize(configDotJson));

    try {
      process = integrationLauncher.discover(jobRoot, WorkerConstants.SOURCE_CONFIG_JSON_FILENAME)
          .start();

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
