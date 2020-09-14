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
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Iterator;
import org.apache.commons.lang3.ArrayUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerTap {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerTap.class);

  @VisibleForTesting
  static final String CONFIG_JSON_FILENAME = "tap_config.json";
  @VisibleForTesting
  static final String CATALOG_JSON_FILENAME = "catalog.json";
  @VisibleForTesting
  static final String STATE_JSON_FILENAME = "input_state.json";
  @VisibleForTesting
  static final String DISCOVERY_DIR = "discover";

  private final String imageName;
  private final ProcessBuilderFactory pbf;
  private final StreamFactory streamFactory;
  private final SingerDiscoverSchemaWorker discoverSchemaWorker;

  private Process tapProcess = null;
  private BufferedReader bufferedReader = null;
  private Iterator<SingerMessage> messageIterator;

  public SingerTap(final String imageName,
                   final ProcessBuilderFactory pbf,
                   final SingerDiscoverSchemaWorker discoverSchemaWorker) {
    this(imageName, pbf, new SingerJsonStreamFactory(), discoverSchemaWorker);
  }

  @VisibleForTesting
  SingerTap(final String imageName,
            final ProcessBuilderFactory pbf,
            final StreamFactory streamFactory,
            final SingerDiscoverSchemaWorker discoverSchemaWorker) {
    this.imageName = imageName;
    this.pbf = pbf;
    this.streamFactory = streamFactory;
    this.discoverSchemaWorker = discoverSchemaWorker;
  }

  public void start(StandardTapConfig input, Path jobRoot) throws IOException, InvalidCredentialsException {
    Preconditions.checkState(tapProcess == null);

    SingerCatalog singerCatalog = runDiscovery(input, jobRoot);

    final JsonNode configDotJson = input.getSourceConnectionImplementation().getConfiguration();

    final SingerCatalog selectedCatalog = SingerCatalogConverters
        .applySchemaToDiscoveredCatalog(singerCatalog, input.getStandardSync().getSchema());

    IOs.writeFile(jobRoot, CONFIG_JSON_FILENAME, Jsons.serialize(configDotJson));
    IOs.writeFile(jobRoot, CATALOG_JSON_FILENAME, Jsons.serialize(selectedCatalog));
    IOs.writeFile(jobRoot, STATE_JSON_FILENAME, Jsons.serialize(input.getState()));

    String[] cmd = {
      "--config",
      CONFIG_JSON_FILENAME,
      // TODO support both --properties and --catalog depending on integration
      "--properties",
      CATALOG_JSON_FILENAME
    };

    if (input.getState() != null) {
      cmd = ArrayUtils.addAll(cmd, "--state", STATE_JSON_FILENAME);
    }

    tapProcess =
        pbf.create(jobRoot, imageName, cmd)
            .redirectError(jobRoot.resolve(SingerSyncWorker.TAP_ERR_LOG).toFile())
            .start();

    bufferedReader = new BufferedReader(new InputStreamReader(tapProcess.getInputStream()));
    messageIterator = streamFactory.create(new BufferedReader(new InputStreamReader(tapProcess.getInputStream()))).iterator();
  }

  public boolean hasNext() {
    Preconditions.checkState(messageIterator != null);
    return messageIterator.hasNext();
  }

  public SingerMessage next() {
    Preconditions.checkState(messageIterator != null);
    return messageIterator.next();
  }

  public void stop() throws IOException {
    Preconditions.checkState(tapProcess != null);

    bufferedReader.close();
    WorkerUtils.cancelProcess(tapProcess);
  }

  private SingerCatalog runDiscovery(StandardTapConfig input, Path jobRoot) throws InvalidCredentialsException, IOException {
    StandardDiscoverSchemaInput discoveryInput = new StandardDiscoverSchemaInput()
        .withConnectionConfiguration(input.getSourceConnectionImplementation().getConfiguration());

    Path discoverJobRoot = jobRoot.resolve(DISCOVERY_DIR);
    Files.createDirectory(discoverJobRoot);

    return discoverSchemaWorker.runInternal(discoveryInput, discoverJobRoot).getOutput().get();
  }

}
