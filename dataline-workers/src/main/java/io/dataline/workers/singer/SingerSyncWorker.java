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
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.apache.commons.lang3.mutable.MutableInt;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerSyncWorker extends BaseSingerWorker<JobSyncOutput> {
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

  private Process workerProcess;

  public SingerSyncWorker(
      String workerId,
      String workspaceRoot,
      String singerRoot,
      SingerTap tap,
      String tapConfiguration,
      String tapCatalog,
      String currentConnectionState,
      SingerTarget target,
      String targetConfig) {
    super(workerId, workspaceRoot, singerRoot);
    this.tap = tap;
    this.tapConfiguration = tapConfiguration;
    this.tapCatalog = tapCatalog;
    this.connectionState = currentConnectionState;
    this.target = target;
    this.targetConfig = targetConfig;
  }

  @Override
  OutputAndStatus<JobSyncOutput> runInternal() {
    String tapConfigPath = writeFileToWorkspace(TAP_CONFIG_FILENAME, tapConfiguration);
    String catalogPath = writeFileToWorkspace(CATALOG_FILENAME, tapCatalog);
    String inputStatePath = writeFileToWorkspace(INPUT_STATE_FILENAME, connectionState);
    String targetConfigPath = writeFileToWorkspace(TARGET_CONFIG_FILENAME, targetConfig);

    MutableInt numRecords = new MutableInt();
    try {
      String[] tapCommand = {
        getExecutableAbsolutePath(tap),
        "--config",
        tapConfigPath,
        "--properties",
        catalogPath,
        "--state",
        inputStatePath
      };
      String[] targetCommand = {getExecutableAbsolutePath(target), "--config", targetConfigPath};
      LOGGER.debug("Tap command: {}", String.join(" ", tapCommand));
      LOGGER.debug("target command: {}", String.join(" ", targetCommand));

      Process tapProcess = new ProcessBuilder().command(tapCommand).start();
      Process targetProcess =
          new ProcessBuilder()
              .command(targetCommand)
              .redirectOutput(getWorkspacePath().resolve(OUTPUT_STATE_FILENAME).toFile())
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
        LOGGER.debug("Waiting for sync worker {} tap.", workerId);
      }

      writer.flush();
      writer.close();
      reader.close();
      while (!targetProcess.waitFor(1, TimeUnit.MINUTES)) {
        LOGGER.debug("Waiting for sync worker {} target", workerId);
      }

      JobSyncOutput jobSyncOutput = new JobSyncOutput();
      State state = new State();
      state.setState(readFileFromWorkspace(OUTPUT_STATE_FILENAME));
      StandardSyncSummary summary = new StandardSyncSummary();
      summary.setRecordsSynced(numRecords.getValue());
      //      summary.set
      // TODO
      summary.setLogs("nothing");
      summary.setAttemptId(UUID.randomUUID());
      summary.setStartTime(1);
      summary.setEndTime(1);
      jobSyncOutput.setState(state);
      jobSyncOutput.setStandardSyncSummary(summary);
      return new OutputAndStatus<>(JobStatus.SUCCESSFUL, jobSyncOutput);
    } catch (IOException | InterruptedException e) {
      // TODO return state
      throw new RuntimeException(e);
    }
  }

  @Override
  public void cancel() {
    cancelHelper(workerProcess);
  }
}
