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
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Charsets;
import io.dataline.config.JobSyncConfig;
import io.dataline.config.JobSyncOutput;
import io.dataline.config.StandardSyncSummary;
import io.dataline.config.State;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.nio.file.Path;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.mutable.MutableInt;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerSyncWorker extends BaseSingerWorker<Void, JobSyncOutput> {
  private static final Logger LOGGER = LoggerFactory.getLogger(SingerSyncWorker.class);

  private static final String TAP_CONFIG_FILENAME = "tap_config.json";
  private static final String CATALOG_FILENAME = "catalog.json";
  private static final String INPUT_STATE_FILENAME = "state.json";
  private static final String TARGET_CONFIG_FILENAME = "target_config.json";

  private static final String OUTPUT_STATE_FILENAME = "outputState.json";
  private static final String TAP_ERR_LOG = "tap_err.log";
  private static final String TARGET_ERR_LOG = "target_err.log";

  private final SingerTap tap;
  private final String tapConfiguration;
  private final String tapCatalog;
  private final String connectionState;
  private final SingerTarget target;
  private final String targetConfig;

  private Process tapReadProcess;
  private Process tapWriteProcess;

  // TODO this needs to all be passed in as part of the input format once we have conversions from
  //  input format to singer format
  public SingerSyncWorker(
      SingerTap tap,
      String tapConfiguration,
      String tapCatalog,
      String currentConnectionState,
      SingerTarget target,
      String targetConfig) {

    this.tap = tap;
    this.tapConfiguration = tapConfiguration;
    this.tapCatalog = tapCatalog;
    this.connectionState = currentConnectionState;
    this.target = target;
    this.targetConfig = targetConfig;
  }

  @Override
  public void cancel() {
    cancelHelper(tapReadProcess);
    cancelHelper(tapWriteProcess);
  }

  @Override
  // TODO fix input format when type conversions exist
  public OutputAndStatus<JobSyncOutput> run(Void nothing, Path workspaceRoot) {
    String tapConfigPath =
        writeFile(workspaceRoot, TAP_CONFIG_FILENAME, tapConfiguration).toAbsolutePath().toString();
    String catalogPath =
        writeFile(workspaceRoot, CATALOG_FILENAME, tapCatalog).toAbsolutePath().toString();
    String inputStatePath =
        writeFile(workspaceRoot, INPUT_STATE_FILENAME, connectionState).toAbsolutePath().toString();
    String targetConfigPath =
        writeFile(workspaceRoot, TARGET_CONFIG_FILENAME, targetConfig).toAbsolutePath().toString();

    MutableInt numRecords = new MutableInt();

    try {
      String[] dockerCmd = {
        "docker", "run", "-v", String.format("%s:/singer/data", workspaceRoot.toString())
      };
      String[] tapCmd =
          ArrayUtils.addAll(
              dockerCmd,
              tap.getImageName(),
              "--config",
              tapConfigPath,
              // TODO support both --properties and --catalog depending on integration
              "--properties",
              catalogPath,
              "--state",
              inputStatePath);

      String[] targetCmd =
          ArrayUtils.addAll(dockerCmd, target.getImageName(), "--config", targetConfigPath);
      LOGGER.debug("Tap command: {}", String.join(" ", tapCmd));
      LOGGER.debug("target command: {}", String.join(" ", targetCmd));

      long startTime = System.currentTimeMillis();
      Process tapProcess = new ProcessBuilder().command(tapCmd).start();
      Process targetProcess =
          new ProcessBuilder()
              .command(targetCmd)
              .redirectOutput(workspaceRoot.resolve(OUTPUT_STATE_FILENAME).toFile())
              .start();

      InputStream tapStdout = tapProcess.getInputStream();
      OutputStream targetStdin = targetProcess.getOutputStream();
      BufferedReader reader = new BufferedReader(new InputStreamReader(tapStdout, Charsets.UTF_8));
      BufferedWriter writer =
          new BufferedWriter(new OutputStreamWriter(targetStdin, Charsets.UTF_8));

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
            "Waiting for sync worker (attemptId:{}) tap.", ""); // TODO when attempt ID is passed in
      }

      // target process stays alive as long as its stdin has not been closed. So we wait for the tap
      // process to end,
      // flush the writer to stdin and close
      writer.flush();
      writer.close();
      reader.close();
      while (!targetProcess.waitFor(1, TimeUnit.MINUTES)) {
        LOGGER.debug(
            "Waiting for sync worker (attemptId:{}) target",
            ""); // TODO when attempt ID is passed in
      }

      JobSyncOutput jobSyncOutput = new JobSyncOutput();
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

      return new OutputAndStatus<>(JobStatus.SUCCESSFUL, jobSyncOutput);
    } catch (IOException | InterruptedException e) {
      // TODO return state
      throw new RuntimeException(e);
    }
  }
}
