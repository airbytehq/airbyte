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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.SingerCatalog;
import io.dataline.config.SingerProtocol;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardTapConfig;
import io.dataline.workers.DefaultSyncWorker;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.SyncTap;
import io.dataline.workers.WorkerUtils;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Iterator;
import java.util.concurrent.TimeUnit;

import org.apache.commons.lang3.ArrayUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerTap implements SyncTap<SingerProtocol> {
  private static final Logger LOGGER = LoggerFactory.getLogger(SingerTap.class);

  private static final String CONFIG_JSON_FILENAME = "tap_config.json";
  private static final String CATALOG_JSON_FILENAME = "catalog.json";

  private static final String STATE_JSON_FILENAME = "input_state.json";

  private final String dockerImageName;

  private Process tapProcess;
  private InputStream stdout;

  public SingerTap(String dockerImageName) {
    this.dockerImageName = dockerImageName;
  }

  @Override
  public Iterator<SingerProtocol> run(StandardTapConfig input, Path workspaceRoot)
      throws InvalidCredentialsException {
    OutputAndStatus<SingerCatalog> discoveryOutput = runDiscovery(input, workspaceRoot);

    final ObjectMapper objectMapper = new ObjectMapper();
    final String configDotJson;
    final String catalogDotJson;
    final String stateDotJson;

    try {
      configDotJson =
          objectMapper.writeValueAsString(
              input.getSourceConnectionImplementation().getConfiguration());
      SingerCatalog selectedCatalog =
          SingerCatalogConverters.applySchemaToDiscoveredCatalog(
              discoveryOutput.getOutput().get(), input.getStandardSync().getSchema());
      catalogDotJson = objectMapper.writeValueAsString(selectedCatalog);
      stateDotJson = objectMapper.writeValueAsString(input.getState());
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }

    // write config.json to disk
    Path configPath =
        WorkerUtils.writeFileToWorkspace(workspaceRoot, CONFIG_JSON_FILENAME, configDotJson);
    Path catalogPath =
        WorkerUtils.writeFileToWorkspace(workspaceRoot, CATALOG_JSON_FILENAME, catalogDotJson);
    Path statePath =
        WorkerUtils.writeFileToWorkspace(workspaceRoot, STATE_JSON_FILENAME, stateDotJson);

    try {

      String[] dockerCmd = SingerDockerUtils.getDockerCommand(workspaceRoot);

      String[] tapCmd =
          ArrayUtils.addAll(
              dockerCmd,
              dockerImageName,
              "--config",
              configPath.toString(),
              // TODO support both --properties and --catalog depending on integration
              "--properties",
              catalogPath.toString(),
              "--state",
              statePath.toString());

      LOGGER.info("running command: {}", Arrays.toString(tapCmd));

      tapProcess =
          new ProcessBuilder()
              .command(tapCmd)
              .redirectError(workspaceRoot.resolve(DefaultSyncWorker.TAP_ERR_LOG).toFile())
              .start();

    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    final InputStream stdout = tapProcess.getInputStream();
    return new SingerJsonIterator(stdout);
  }

  @Override
  public void cancel() {
    WorkerUtils.cancelHelper(tapProcess);
  }

  @Override
  public void close() {
    if (stdout != null) {
      try {
        stdout.close();
      } catch (IOException e) {
        throw new RuntimeException();
      }
    }

    if (tapProcess != null) {
      try {
        while (!tapProcess.waitFor(1, TimeUnit.MINUTES)) {
          LOGGER.debug(
              "Waiting for sync worker (job:{}) target", ""); // TODO when job id is passed in
        }
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
  }

  private OutputAndStatus<SingerCatalog> runDiscovery(StandardTapConfig input, Path workspaceRoot)
      throws InvalidCredentialsException {
    StandardDiscoverSchemaInput discoveryInput = new StandardDiscoverSchemaInput();
    discoveryInput.setConnectionConfiguration(
        input.getSourceConnectionImplementation().getConfiguration());
    Path scopedWorkspace = workspaceRoot.resolve("discovery");
    return new SingerDiscoverSchemaWorker(dockerImageName)
        .runInternal(discoveryInput, scopedWorkspace);
  }
}
