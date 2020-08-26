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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Charsets;
import io.dataline.config.SingerCatalog;
import io.dataline.config.StandardDiscoverSchemaInput;
import io.dataline.config.StandardSyncInput;
import io.dataline.config.StandardSyncOutput;
import io.dataline.config.StandardSyncSummary;
import io.dataline.config.State;
import io.dataline.workers.InvalidCredentialsException;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.file.Path;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.mutable.MutableInt;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerSyncWorker extends BaseSingerWorker<StandardSyncInput, StandardSyncOutput> {
  private static final Logger LOGGER = LoggerFactory.getLogger(SingerSyncWorker.class);

  private static final String TAP_CONFIG_FILENAME = "tap_config.json";
  private static final String CATALOG_FILENAME = "catalog.json";
  private static final String INPUT_STATE_FILENAME = "input_state.json";
  private static final String TARGET_CONFIG_FILENAME = "target_config.json";

  private static final String OUTPUT_STATE_FILENAME = "output_state.json";
  private static final String TAP_ERR_LOG = "tap_err.log";
  private static final String TARGET_ERR_LOG = "target_err.log";

  private final SingerTap tap;
  private final SingerTarget target;

  private Process tapProcess;
  private Process targetProcess;

  public SingerSyncWorker(SingerTap tap, SingerTarget target) {
    this.tap = tap;
    this.target = target;
  }

  @Override
  public void cancel() {
    cancelHelper(tapProcess);
    cancelHelper(targetProcess);
  }

  @Override
  public OutputAndStatus<StandardSyncOutput> run(StandardSyncInput input, Path workspaceRoot)
      throws InvalidCredentialsException {

    OutputAndStatus<SingerCatalog> discoveryOutput = runDiscovery(input, workspaceRoot);
    if (discoveryOutput.getStatus() != SUCCESSFUL || discoveryOutput.getOutput().isEmpty()) {
      LOGGER.debug(
          "Sync worker failed due to failed discovery. Discovery output: {}", discoveryOutput);
      return new OutputAndStatus<>(FAILED);
    }

    try {
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
              CATALOG_FILENAME);
      //              "--state",
      //              INPUT_STATE_FILENAME);

      String[] targetCmd =
          ArrayUtils.addAll(dockerCmd, target.getImageName(), "--config", TARGET_CONFIG_FILENAME);
      LOGGER.debug("Tap command: {}", String.join(" ", tapCmd));
      LOGGER.debug("target command: {}", String.join(" ", targetCmd));

      long startTime = System.currentTimeMillis();
      tapProcess =
          new ProcessBuilder()
              .command(tapCmd)
              .redirectError(workspaceRoot.resolve(TAP_ERR_LOG).toFile())
              .start();
      targetProcess =
          new ProcessBuilder()
              .command(targetCmd)
              .redirectOutput(workspaceRoot.resolve(OUTPUT_STATE_FILENAME).toFile())
              .redirectError(workspaceRoot.resolve(TARGET_ERR_LOG).toFile())
              .start();

      try (BufferedReader reader =
              new BufferedReader(
                  new InputStreamReader(tapProcess.getInputStream(), Charsets.UTF_8));
          BufferedWriter writer =
              new BufferedWriter(
                  new OutputStreamWriter(targetProcess.getOutputStream(), Charsets.UTF_8)); ) {
        ObjectMapper objectMapper = new ObjectMapper();
        reader
            .lines()
            .forEach(
                line -> {
                  try {
                    writer.write(line);
                    writer.newLine();
                    JsonNode lineJson = objectMapper.readTree(line);
                    if (lineJson.get("type").asText().equals("RECORD")) {
                      numRecords.increment();
                    }
                  } catch (IOException e) {
                    throw new RuntimeException(e);
                  }
                });

        while (!tapProcess.waitFor(1, TimeUnit.MINUTES)) {
          LOGGER.debug(
              "Waiting for sync worker (attemptId:{}) tap.",
              ""); // TODO when attempt ID is passed in
        }
      }

      // target process stays alive as long as its stdin has not been closed
      while (!targetProcess.waitFor(1, TimeUnit.MINUTES)) {
        LOGGER.debug(
            "Waiting for sync worker (attemptId:{}) target",
            ""); // TODO when attempt ID is passed in
      }

      StandardSyncOutput jobSyncOutput = new StandardSyncOutput();
      StandardSyncSummary summary = new StandardSyncSummary();
      summary.setRecordsSynced(numRecords.getValue().longValue());
      summary.setStartTime(startTime);
      summary.setEndTime(System.currentTimeMillis());
      summary.setJobId(UUID.randomUUID()); // TODO this is not input anywhere
      // TODO set logs
      jobSyncOutput.setStandardSyncSummary(summary);

      State state = new State();
      state.setState(readFile(workspaceRoot, OUTPUT_STATE_FILENAME));
      jobSyncOutput.setState(state);

      JobStatus status =
          tapProcess.exitValue() == 0 && targetProcess.exitValue() == 0 ? SUCCESSFUL : FAILED;

      if (status == FAILED) {
        LOGGER.debug(
            "Sync worker failed. Tap error log: {}.\n Target error log: {}",
            readFile(workspaceRoot, TAP_ERR_LOG),
            readFile(workspaceRoot, TARGET_ERR_LOG));
      }
      return new OutputAndStatus<>(status, jobSyncOutput);
    } catch (IOException | InterruptedException e) {
      // TODO return state
      throw new RuntimeException(e);
    }
  }

  private OutputAndStatus<SingerCatalog> runDiscovery(StandardSyncInput input, Path workspaceRoot)
      throws InvalidCredentialsException {
    StandardDiscoverSchemaInput discoveryInput = new StandardDiscoverSchemaInput();
    discoveryInput.setConnectionConfiguration(
        input.getSourceConnectionImplementation().getConfiguration());
    Path scopedWorkspace = workspaceRoot.resolve("discovery");
    OutputAndStatus<SingerCatalog> discoveryOutput =
        new SingerDiscoverSchemaWorker(tap).runInternal(discoveryInput, scopedWorkspace);
    return discoveryOutput;
  }

  private void writeSingerInputsToDisk(
      StandardSyncInput input, Path workspaceRoot, SingerCatalog tapCatalog)
      throws JsonProcessingException {
    // TODO configuration should be validated against the connector's spec then converted to the
    //  connector-appropriate format. right now this assumes the object is a valid JSON for this
    //  connector.
    ObjectMapper objectMapper = new ObjectMapper();
    String tapConfiguration =
        objectMapper.writeValueAsString(
            input.getSourceConnectionImplementation().getConfiguration());
    String targetConfiguration =
        objectMapper.writeValueAsString(
            input.getDestinationConnectionImplementation().getConfiguration());
    String stateString = objectMapper.writeValueAsString(input.getState().getState());

    writeFile(workspaceRoot, TAP_CONFIG_FILENAME, tapConfiguration);
    writeFile(workspaceRoot, CATALOG_FILENAME, objectMapper.writeValueAsString(tapCatalog));
    writeFile(workspaceRoot, INPUT_STATE_FILENAME, stateString);
    writeFile(workspaceRoot, TARGET_CONFIG_FILENAME, targetConfiguration);
  }
}
