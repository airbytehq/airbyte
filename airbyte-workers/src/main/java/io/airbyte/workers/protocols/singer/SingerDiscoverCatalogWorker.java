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

package io.airbyte.workers.protocols.singer;

import static io.airbyte.workers.JobStatus.FAILED;
import static io.airbyte.workers.JobStatus.SUCCEEDED;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.singer.SingerCatalog;
import io.airbyte.workers.DiscoverCatalogWorker;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.IOException;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerDiscoverCatalogWorker implements DiscoverCatalogWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerDiscoverCatalogWorker.class);

  private final IntegrationLauncher integrationLauncher;

  private volatile Process process;

  public SingerDiscoverCatalogWorker(final IntegrationLauncher integrationLauncher) {
    this.integrationLauncher = integrationLauncher;
  }

  @Override
  public OutputAndStatus<StandardDiscoverCatalogOutput> run(final StandardDiscoverCatalogInput discoverSchemaInput,
                                                            final Path jobRoot) {
    try {
      return runInternal(discoverSchemaInput, jobRoot);
    } catch (final Exception e) {
      LOGGER.error("Error while discovering schema", e);
      return new OutputAndStatus<>(FAILED);
    }
  }

  private OutputAndStatus<StandardDiscoverCatalogOutput> runInternal(final StandardDiscoverCatalogInput discoverSchemaInput,
                                                                     final Path jobRoot)
      throws IOException, WorkerException {
    final JsonNode configDotJson = discoverSchemaInput.getConnectionConfiguration();

    IOs.writeFile(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME, Jsons.serialize(configDotJson));

    process = integrationLauncher.discover(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME)
        // TODO: we shouldn't trust the tap does not pollute stdout
        .redirectOutput(jobRoot.resolve(WorkerConstants.CATALOG_JSON_FILENAME).toFile())
        .start();

    LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

    WorkerUtils.gentleClose(process, 1, TimeUnit.MINUTES);

    int exitCode = process.exitValue();

    if (exitCode == 0) {
      return new OutputAndStatus<>(
          SUCCEEDED,
          new StandardDiscoverCatalogOutput()
              .withSchema(SingerCatalogConverters.toAirbyteSchema(readCatalog(jobRoot))));
    } else {
      LOGGER.debug("Discovery job subprocess finished with exit code {}", exitCode);
      return new OutputAndStatus<>(FAILED);
    }
  }

  @Override
  public void cancel() {
    WorkerUtils.cancelProcess(process);
  }

  public static SingerCatalog readCatalog(Path jobRoot) {
    return Jsons.deserialize(IOs.readFile(jobRoot, WorkerConstants.CATALOG_JSON_FILENAME), SingerCatalog.class);
  }

}
