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
import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardTapConfig;
import io.dataline.singer.SingerCatalog;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.StreamFactory;
import io.dataline.workers.WorkerConstants;
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

  private final String imageName;
  private final ProcessBuilderFactory pbf;
  private final StreamFactory streamFactory;
  private final SingerDiscoverSchemaWorker discoverSchemaWorker;

  private Process tapProcess = null;
  private Iterator<SingerMessage> messageIterator = null;

  public DefaultSingerTap(final String imageName,
                          final ProcessBuilderFactory pbf,
                          final SingerDiscoverSchemaWorker discoverSchemaWorker) {
    this(imageName, pbf, new SingerJsonStreamFactory(), discoverSchemaWorker);
  }

  @VisibleForTesting
  DefaultSingerTap(final String imageName,
                   final ProcessBuilderFactory pbf,
                   final StreamFactory streamFactory,
                   final SingerDiscoverSchemaWorker discoverSchemaWorker) {
    this.imageName = imageName;
    this.pbf = pbf;
    this.streamFactory = streamFactory;
    this.discoverSchemaWorker = discoverSchemaWorker;
  }

  @Override
  public void start(StandardTapConfig input, Path jobRoot) throws IOException, InvalidCredentialsException {
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
      WorkerConstants.TAP_CONFIG_JSON_FILENAME,
      // TODO support both --properties and --catalog depending on integration
      "--properties",
      WorkerConstants.CATALOG_JSON_FILENAME
    };

    if (input.getState() != null) {
      cmd = ArrayUtils.addAll(cmd, "--state", WorkerConstants.INPUT_STATE_JSON_FILENAME);
    }

    tapProcess =
        pbf.create(jobRoot, imageName, cmd)
            .redirectError(jobRoot.resolve(WorkerConstants.TAP_ERR_LOG).toFile())
            .start();

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
      throw new Exception("Tap process wasn't successful");
    }
  }

  private SingerCatalog runDiscovery(StandardTapConfig input, Path jobRoot) throws InvalidCredentialsException, IOException {
    StandardDiscoverSchemaInput discoveryInput = new StandardDiscoverSchemaInput()
        .withConnectionConfiguration(input.getSourceConnectionImplementation().getConfiguration());

    final Optional<SingerCatalog> output = discoverSchemaWorker.runInternal(discoveryInput, jobRoot).getOutput();
    // We are going to write the catalog to be used in sync to this location. Instead of
    // overwriting, retain the returned schema for debugging purposes.
    final Path catalogPath = jobRoot.resolve(WorkerConstants.CATALOG_JSON_FILENAME);
    if (Files.exists(catalogPath)) {
      Files.move(catalogPath, jobRoot.resolve(WorkerConstants.ORIGINAL_CATALOG_JSON_FILENAME));
    }

    return output.orElseThrow(() -> new IOException("Failed to discover schema."));
  }

}
