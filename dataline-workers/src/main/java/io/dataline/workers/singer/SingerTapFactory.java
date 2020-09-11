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
import io.dataline.commons.io.IOs;
import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardTapConfig;
import io.dataline.singer.SingerCatalog;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.DefaultSyncWorker;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.StreamFactory;
import io.dataline.workers.TapFactory;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import io.dataline.workers.protocol.singer.SingerJsonStreamFactory;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.stream.Stream;
import org.apache.commons.lang3.ArrayUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerTapFactory implements TapFactory<SingerMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingerTapFactory.class);

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

  public SingerTapFactory(final String imageName,
                          final ProcessBuilderFactory pbf,
                          final SingerDiscoverSchemaWorker discoverSchemaWorker) {
    this(imageName, pbf, new SingerJsonStreamFactory(), discoverSchemaWorker);
  }

  @VisibleForTesting
  SingerTapFactory(final String imageName,
                   final ProcessBuilderFactory pbf,
                   final StreamFactory streamFactory,
                   final SingerDiscoverSchemaWorker discoverSchemaWorker) {
    this.imageName = imageName;
    this.pbf = pbf;
    this.streamFactory = streamFactory;
    this.discoverSchemaWorker = discoverSchemaWorker;
  }

  @Override
  public Stream<SingerMessage> create(StandardTapConfig input, Path jobRoot) throws InvalidCredentialsException {
    OutputAndStatus<SingerCatalog> discoveryOutput = runDiscovery(input, jobRoot);

    final JsonNode configDotJson = input.getSourceConnectionImplementation().getConfiguration();

    final SingerCatalog selectedCatalog = SingerCatalogConverters.applySchemaToDiscoveredCatalog(
        discoveryOutput.getOutput().get(), input.getStandardSync().getSchema());
    final String catalogDotJson = Jsons.serialize(selectedCatalog);
    final String stateDotJson = Jsons.serialize(input.getState());

    IOs.writeFile(jobRoot, CONFIG_JSON_FILENAME, Jsons.serialize(configDotJson));
    IOs.writeFile(jobRoot, CATALOG_JSON_FILENAME, catalogDotJson);
    IOs.writeFile(jobRoot, STATE_JSON_FILENAME, stateDotJson);

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

    try {
      tapProcess =
          pbf.create(
              jobRoot,
              imageName,
              cmd)
              .redirectError(jobRoot.resolve(DefaultSyncWorker.TAP_ERR_LOG).toFile())
              .start();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    bufferedReader = new BufferedReader(new InputStreamReader(tapProcess.getInputStream()));

    return streamFactory.create(bufferedReader).onClose(getCloseFunction());
  }

  public Runnable getCloseFunction() {
    return () -> {
      if (bufferedReader != null) {
        try {
          bufferedReader.close();
        } catch (IOException e) {
          throw new RuntimeException(e);
        }
      }

      WorkerUtils.cancelProcess(tapProcess);
    };
  }

  private OutputAndStatus<SingerCatalog> runDiscovery(StandardTapConfig input, Path jobRoot)
      throws InvalidCredentialsException {
    StandardDiscoverSchemaInput discoveryInput = new StandardDiscoverSchemaInput()
        .withConnectionConfiguration(input.getSourceConnectionImplementation().getConfiguration());
    Path discoverJobRoot = jobRoot.resolve(DISCOVERY_DIR);
    try {
      Files.createDirectory(discoverJobRoot);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    return discoverSchemaWorker.runInternal(discoveryInput, discoverJobRoot);
  }

}
