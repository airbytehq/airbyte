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

package io.dataline.workers.protocols.singer;

import static io.dataline.workers.JobStatus.FAILED;
import static io.dataline.workers.JobStatus.SUCCESSFUL;

import com.fasterxml.jackson.databind.JsonNode;
import io.dataline.commons.io.IOs;
import io.dataline.commons.io.LineGobbler;
import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.singer.SingerCatalog;
import io.dataline.workers.DiscoverSchemaWorker;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.WorkerConstants;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerDiscoverSchemaWorker implements DiscoverSchemaWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerDiscoverSchemaWorker.class);

  private final String imageName;
  private final ProcessBuilderFactory pbf;

  private volatile Process process;

  public SingerDiscoverSchemaWorker(final String imageName, final ProcessBuilderFactory pbf) {
    this.imageName = imageName;
    this.pbf = pbf;
  }

  @Override
  public OutputAndStatus<StandardDiscoverSchemaOutput> run(final StandardDiscoverSchemaInput discoverSchemaInput,
                                                           final Path jobRoot) {
    try {
      return runInternal(discoverSchemaInput, jobRoot);
    } catch (final Exception e) {
      LOGGER.error("Error while discovering schema", e);
      return new OutputAndStatus<>(FAILED);
    }
  }

  private OutputAndStatus<StandardDiscoverSchemaOutput> runInternal(final StandardDiscoverSchemaInput discoverSchemaInput,
                                                                    final Path jobRoot)
      throws IOException {
    final JsonNode configDotJson = discoverSchemaInput.getConnectionConfiguration();

    IOs.writeFile(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME, Jsons.serialize(configDotJson));

    process = pbf.create(jobRoot, imageName, "--config", WorkerConstants.TAP_CONFIG_JSON_FILENAME, "--discover")
        // TODO: we shouldn't trust the tap not not pollute stdout
        .redirectOutput(jobRoot.resolve(WorkerConstants.CATALOG_JSON_FILENAME).toFile())
        .start();

    LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

    WorkerUtils.gentleClose(process, 1, TimeUnit.MINUTES);

    int exitCode = process.exitValue();

    if (exitCode == 0) {
      final SingerCatalog catalog = readCatalog(jobRoot);
      return new OutputAndStatus<>(
          SUCCESSFUL,
          new StandardDiscoverSchemaOutput()
              .withSchema(SingerCatalogConverters.toDatalineSchema(catalog)));
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
