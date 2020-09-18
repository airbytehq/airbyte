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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.dataline.commons.io.IOs;
import io.dataline.commons.io.LineGobbler;
import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.config.StandardTapConfig;
import io.dataline.singer.SingerCatalog;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.WorkerConstants;
import io.dataline.workers.WorkerException;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Iterator;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.ArrayUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSingerTap implements SingerTap {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSingerTap.class);

  @VisibleForTesting
  static final String DISCOVERY_DIR = "discover";

  private final String imageName;
  private final ProcessBuilderFactory pbf;
  private final SingerStreamFactory streamFactory;
  private final SingerDiscoverSchemaWorker discoverSchemaWorker;

  private Process tapProcess = null;
  private Iterator<SingerMessage> messageIterator = null;

  public DefaultSingerTap(final String imageName,
                          final ProcessBuilderFactory pbf,
                          final SingerDiscoverSchemaWorker discoverSchemaWorker) {
    this(imageName, pbf, new DefaultSingerStreamFactory(), discoverSchemaWorker);
  }

  @VisibleForTesting
  DefaultSingerTap(final String imageName,
                   final ProcessBuilderFactory pbf,
                   final SingerStreamFactory streamFactory,
                   final SingerDiscoverSchemaWorker discoverSchemaWorker) {
    this.imageName = imageName;
    this.pbf = pbf;
    this.streamFactory = streamFactory;
    this.discoverSchemaWorker = discoverSchemaWorker;
  }

  @Override
  public void start(StandardTapConfig input, Path jobRoot) throws Exception {
    Preconditions.checkState(tapProcess == null);

    SingerCatalog singerCatalog = runDiscovery(input, jobRoot);

    final JsonNode configDotJson = input.getSourceConnectionImplementation().getConfiguration();

    final SingerCatalog selectedCatalog = SingerCatalogConverters
        .applySchemaToDiscoveredCatalog(singerCatalog, input.getStandardSync().getSchema());

    IOs.writeFile(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME, Jsons.serialize(configDotJson));
    IOs.writeFile(jobRoot, WorkerConstants.CATALOG_JSON_FILENAME, Jsons.serialize(selectedCatalog));
    IOs.writeFile(jobRoot, WorkerConstants.INPUT_STATE_JSON_FILENAME, Jsons.serialize(input.getState()));

    String[] cmd = {
      "--config",
      jobRoot.resolve(WorkerConstants.TAP_CONFIG_JSON_FILENAME).toString(),
      // TODO support both --properties and --catalog depending on integration
      "--properties",
      jobRoot.resolve(WorkerConstants.CATALOG_JSON_FILENAME).toString()
    };

    if (input.getState() != null) {
      cmd = ArrayUtils.addAll(cmd, "--state", WorkerConstants.INPUT_STATE_JSON_FILENAME);
    }

    tapProcess = pbf.create(jobRoot, imageName, cmd).start();
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
  public Optional<SingerMessage> attemptRead() {
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

  private SingerCatalog runDiscovery(StandardTapConfig input, Path jobRoot) throws IOException, WorkerException {
    StandardDiscoverSchemaInput discoveryInput = new StandardDiscoverSchemaInput()
        .withConnectionConfiguration(input.getSourceConnectionImplementation().getConfiguration());

    Path discoverJobRoot = jobRoot.resolve(DISCOVERY_DIR);
    Files.createDirectory(discoverJobRoot);

    final OutputAndStatus<StandardDiscoverSchemaOutput> output = discoverSchemaWorker.run(discoveryInput, discoverJobRoot);
    if (output.getStatus() == JobStatus.FAILED) {
      throw new WorkerException("Cannot discover schema");
    }

    // This is a hack because we need to have access to the original singer catalog
    return SingerDiscoverSchemaWorker.readCatalog(discoverJobRoot);
  }

}
