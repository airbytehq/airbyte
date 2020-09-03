/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.workers.singer;

import static io.dataline.workers.JobStatus.FAILED;
import static io.dataline.workers.JobStatus.SUCCESSFUL;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.dataline.commons.io.IOs;
import io.dataline.commons.json.Jsons;
import io.dataline.config.Schema;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.singer.SingerCatalog;
import io.dataline.workers.DiscoverSchemaWorker;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerDiscoverSchemaWorker implements DiscoverSchemaWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerDiscoverSchemaWorker.class);

  // TODO log errors to specified file locations
  @VisibleForTesting
  static final String CONFIG_JSON_FILENAME = "config.json";
  static final String CATALOG_JSON_FILENAME = "catalog.json";
  static final String ERROR_LOG_FILENAME = "err.log";

  private final String imageName;
  private final ProcessBuilderFactory pbf;

  private volatile Process workerProcess;

  public SingerDiscoverSchemaWorker(final String imageName, final ProcessBuilderFactory pbf) {
    this.imageName = imageName;
    this.pbf = pbf;
  }

  // package private since package-local classes need direct access to singer catalog, and the
  // conversion from SingerSchema to Dataline schema is lossy
  OutputAndStatus<SingerCatalog> runInternal(StandardDiscoverSchemaInput discoverSchemaInput, Path jobRoot) throws InvalidCredentialsException {
    // todo (cgardens) - just getting original impl to line up with new iface for now. this can be
    // reduced.
    final JsonNode configDotJson = discoverSchemaInput.getConnectionConfiguration();

    IOs.writeFile(jobRoot, CONFIG_JSON_FILENAME, Jsons.serialize(configDotJson));

    // exec
    try {
      workerProcess =
          pbf.create(jobRoot, imageName, "--config", CONFIG_JSON_FILENAME, "--discover")
              .redirectError(jobRoot.resolve(ERROR_LOG_FILENAME).toFile())
              .redirectOutput(jobRoot.resolve(CATALOG_JSON_FILENAME).toFile())
              .start();

      while (!workerProcess.waitFor(1, TimeUnit.MINUTES)) {
        LOGGER.info("Waiting for discovery job.");
      }

      int exitCode = workerProcess.exitValue();
      if (exitCode == 0) {
        final String catalog = IOs.readFile(jobRoot, CATALOG_JSON_FILENAME);
        return new OutputAndStatus<>(SUCCESSFUL, Jsons.deserialize(catalog, SingerCatalog.class));
      } else {
        // TODO throw invalid credentials exception where appropriate based on error log
        String errLog = IOs.readFile(jobRoot, ERROR_LOG_FILENAME);
        LOGGER.debug(
            "Discovery job subprocess finished with exit code {}. Error log: {}", exitCode, errLog);
        return new OutputAndStatus<>(FAILED);
      }
    } catch (IOException | InterruptedException e) {
      LOGGER.error("Exception running discovery: ", e);
      throw new RuntimeException(e);
    }
  }

  @Override
  public OutputAndStatus<StandardDiscoverSchemaOutput> run(StandardDiscoverSchemaInput discoverSchemaInput, Path jobRoot)
      throws InvalidCredentialsException {
    OutputAndStatus<SingerCatalog> output = runInternal(discoverSchemaInput, jobRoot);
    JobStatus status = output.getStatus();

    if (output.getOutput().isPresent()) {
      return new OutputAndStatus<>(status, toDiscoveryOutput(output.getOutput().get()));
    } else {
      return new OutputAndStatus<>(status);
    }
  }

  private static StandardDiscoverSchemaOutput toDiscoveryOutput(SingerCatalog catalog) {
    final Schema schema = SingerCatalogConverters.toDatalineSchema(catalog);
    final StandardDiscoverSchemaOutput output = new StandardDiscoverSchemaOutput();
    output.withSchema(schema);

    return output;
  }

  @Override
  public void cancel() {
    WorkerUtils.cancelProcess(workerProcess);
  }

}
