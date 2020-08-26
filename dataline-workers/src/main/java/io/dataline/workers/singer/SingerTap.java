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
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardTapConfig;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.SyncTap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.Iterator;

public class SingerTap implements SyncTap<SingerProtocol> {
  private static Logger LOGGER = LoggerFactory.getLogger(SingerProtocol.class);
  private static String CONFIG_JSON_FILENAME = "config.json";
  private static String CATALOG_JSON_FILENAME = "catalog.json";
  private static String STATE_JSON_FILENAME = "input_state.json";
  private static String ERROR_LOG_FILENAME = "err.log";

  private final SingerConnector singerConnector;

  public SingerTap(SingerConnector singerConnector) {
    this.singerConnector = singerConnector;
  }

  SingerCatalog selectedCatalog =
    SingerCatalogConverters.applySchemaToDiscoveredCatalog(
      discoveryOutput.getOutput().get(), input.getStandardSync().getSchema());
  writeSingerInputsToDisk(input, workspaceRoot, selectedCatalog);
  MutableInt numRecords = new MutableInt();

  String[] dockerCmd = {
    "docker",
    "run",
    "-v",
    String.format("%s:/singer/data", workspaceRoot.toString()),
    // TODO network=host is not recommended for production settings, create a bridge network
    //  and use it to connect all containers
    "--network=host"
  };

  String[] tapCmd =
    ArrayUtils.addAll(
      dockerCmd,
      tap.getImageName(),
      "--config",
      TAP_CONFIG_FILENAME,
      // TODO support both --properties and --catalog depending on integration
      "--properties",
      CATALOG_FILENAME,
      "--state",
      INPUT_STATE_FILENAME);


  @SuppressWarnings("UnstableApiUsage")
  @Override
  public Iterator<SingerProtocol> run(StandardTapConfig tapConfig, Path workspaceRoot) {

    OutputAndStatus<SingerCatalog> discoveryOutput = runDiscovery(input, workspaceRoot);
    // todo (cgardens) - just getting original impl to line up with new iface for now. this can be
    //   reduced.
    final ObjectMapper objectMapper = new ObjectMapper();
    final String configDotJson;
    final String catalogDotJson;
    final String stateDotJson;
    try {
      configDotJson =
          objectMapper.writeValueAsString(
              tapConfig.getSourceConnectionImplementation().getConfiguration());
      SingerCatalog selectedCatalog =
        SingerCatalogConverters.applySchemaToDiscoveredCatalog(
          discoveryOutput.getOutput().get(), tapConfig.getStandardSync().getSchema());
      catalogDotJson =
          objectMapper.writeValueAsString(selectedCatalog);
      stateDotJson = objectMapper.writeValueAsString(tapConfig.getState());
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }

    // write config.json to disk
    String configPath = writeFileToWorkspace(workspaceRoot, CONFIG_JSON_FILENAME, configDotJson);
    String catalogPath = writeFileToWorkspace(workspaceRoot, CATALOG_JSON_FILENAME, catalogDotJson);
    String statePath = writeFileToWorkspace(workspaceRoot, STATE_JSON_FILENAME, stateDotJson);

    Process tapProcess = null;
    try {
      tapProcess =
          new ProcessBuilder()
              .command(
                  singerExecutablePath,
                  "--config",
                  configPath,
                  "--catalog",
                  catalogPath,
                  "--state",
                  statePath)
              .start();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    final InputStream stdout = tapProcess.getInputStream();

    return new SingerJsonIterator(stdout);
  }

  // todo (cgardens) - copy pasta for now. if we go this round move this out of BaseSingerWorker
  // into a helper.
  protected String writeFileToWorkspace(Path workspaceRoot, String fileName, String contents) {
    String filePath = getWorkspaceFilePath(workspaceRoot, fileName);
    try (FileWriter fileWriter = new FileWriter(filePath)) {
      fileWriter.write(contents);
      return filePath;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private String getWorkspaceFilePath(Path workspaceRoot, String fileName) {
    return workspaceRoot.resolve(fileName).toAbsolutePath().toString();
  }

  private OutputAndStatus<SingerCatalog> runDiscovery(StandardSyncInput input, Path workspaceRoot)
    throws InvalidCredentialsException {
    StandardDiscoverSchemaInput discoveryInput = new StandardDiscoverSchemaInput();
    discoveryInput.setConnectionConfiguration(
      input.getSourceConnectionImplementation().getConfiguration());
    Path scopedWorkspace = workspaceRoot.resolve("discovery");
    OutputAndStatus<SingerCatalog> discoveryOutput =
      new SingerDiscoverSchemaWorker(singerConnector).runInternal(discoveryInput, scopedWorkspace);
    return discoveryOutput;
  }
}
