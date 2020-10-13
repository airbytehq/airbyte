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

package io.airbyte.workers.protocols.airbyte;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.DiscoverCatalogWorker;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Iterator;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultAirbyteSource implements AirbyteSource {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultAirbyteSource.class);

  @VisibleForTesting
  static final String DISCOVERY_DIR = "discover";

  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;
  private final DiscoverCatalogWorker discoverCatalogWorker;

  private Process tapProcess = null;
  private Iterator<AirbyteMessage> messageIterator = null;

  public DefaultAirbyteSource(final IntegrationLauncher integrationLauncher,
                              final DiscoverCatalogWorker discoverSchemaWorker) {
    this(integrationLauncher, new DefaultAirbyteStreamFactory(), discoverSchemaWorker);
  }

  @VisibleForTesting
  DefaultAirbyteSource(final IntegrationLauncher integrationLauncher,
                       final AirbyteStreamFactory streamFactory,
                       final DiscoverCatalogWorker discoverSchemaWorker) {
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
    this.discoverCatalogWorker = discoverSchemaWorker;
  }

  @Override
  public void start(StandardTapConfig input, Path jobRoot) throws Exception {
    Preconditions.checkState(tapProcess == null);

    AirbyteCatalog catalog = runDiscovery(input, jobRoot);

    final JsonNode configDotJson = input.getSourceConnectionImplementation().getConfiguration();

    IOs.writeFile(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME, Jsons.serialize(configDotJson));
    IOs.writeFile(jobRoot, WorkerConstants.CATALOG_JSON_FILENAME, Jsons.serialize(catalog));
    IOs.writeFile(jobRoot, WorkerConstants.INPUT_STATE_JSON_FILENAME, Jsons.serialize(input.getState()));

    tapProcess = integrationLauncher.read(jobRoot,
        WorkerConstants.TAP_CONFIG_JSON_FILENAME,
        WorkerConstants.CATALOG_JSON_FILENAME,
        input.getState() == null ? null : WorkerConstants.INPUT_STATE_JSON_FILENAME).start();
    // stdout logs are logged elsewhere since stdout also contains data
    LineGobbler.gobble(tapProcess.getErrorStream(), LOGGER::error);

    messageIterator = streamFactory.create(IOs.newBufferedReader(tapProcess.getInputStream())).iterator();
  }

  @Override
  public boolean isFinished() {
    Preconditions.checkState(tapProcess != null);

    return !tapProcess.isAlive() && !messageIterator.hasNext();
  }

  @Override
  public Optional<AirbyteMessage> attemptRead() {
    Preconditions.checkState(tapProcess != null);

    return Optional.ofNullable(messageIterator.hasNext() ? messageIterator.next() : null);
  }

  @Override
  public void close() throws Exception {
    if (tapProcess == null) {
      return;
    }

    LOGGER.debug("Closing tap process");
    WorkerUtils.gentleClose(tapProcess, 1, TimeUnit.MINUTES);
    if (tapProcess.isAlive() || tapProcess.exitValue() != 0) {
      throw new WorkerException("Tap process wasn't successful");
    }
  }

  private AirbyteCatalog runDiscovery(StandardTapConfig input, Path jobRoot) throws IOException, WorkerException {
    StandardDiscoverCatalogInput discoveryInput = new StandardDiscoverCatalogInput()
        .withConnectionConfiguration(input.getSourceConnectionImplementation().getConfiguration());

    Path discoverJobRoot = jobRoot.resolve(DISCOVERY_DIR);
    Files.createDirectory(discoverJobRoot);

    final OutputAndStatus<StandardDiscoverCatalogOutput> output = discoverCatalogWorker.run(discoveryInput, discoverJobRoot);
    if (output.getStatus() == JobStatus.FAILED || output.getOutput().isEmpty()) {
      throw new WorkerException("Cannot discover schema");
    }

    return output.getOutput().get().getCatalog();
  }

}
