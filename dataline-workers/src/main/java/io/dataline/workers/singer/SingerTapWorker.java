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
import com.google.common.collect.Streams;
import io.dataline.config.JobSyncTapConfig;
import io.dataline.workers.SyncTap;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.Iterator;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingerTapWorker implements SyncTap<SingerProtocol> {
  private static Logger LOGGER = LoggerFactory.getLogger(SingerProtocol.class);
  private static String CONFIG_JSON_FILENAME = "config.json";
  private static String CATALOG_JSON_FILENAME = "catalog.json";
  private static String STATE_JSON_FILENAME = "input_state.json";
  private static String ERROR_LOG_FILENAME = "err.log";

  private String singerExecutablePath;

  public SingerTapWorker(String singerExecutablePath) {
    this.singerExecutablePath = singerExecutablePath;
  }

  @SuppressWarnings("UnstableApiUsage")
  @Override
  public Stream<SingerProtocol> run(JobSyncTapConfig jobSyncTapConfig, String workspaceRoot) {
    // todo (cgardens) - just getting original impl to line up with new iface for now. this can be
    //   reduced.
    final ObjectMapper objectMapper = new ObjectMapper();
    final String configDotJson;
    final String catalogDotJson;
    final String stateDotJson;
    try {
      configDotJson =
          objectMapper.writeValueAsString(
              jobSyncTapConfig.getSourceConnectionImplementation().getConfiguration());
      catalogDotJson =
          objectMapper.writeValueAsString(
              jobSyncTapConfig
                  .getStandardSync()
                  .getName()); // todo (cgardens) - convert to singer catalog.
      stateDotJson = jobSyncTapConfig.getState()); // todo (cgardens) - add this to the config!!!
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

    final Iterator<SingerProtocol> singerJsonIterator = new SingerJsonIterator(stdout);
    return Streams.stream(singerJsonIterator);
  }

  // todo (cgardens) - copy pasta for now. if we go this round move this out of BaseSingerWorker
  // into a helper.
  protected String writeFileToWorkspace(String workspaceRoot, String fileName, String contents) {
    String filePath = getWorkspaceFilePath(workspaceRoot, fileName);
    try (FileWriter fileWriter = new FileWriter(filePath)) {
      fileWriter.write(contents);
      return filePath;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private String getWorkspaceFilePath(String workspaceRoot, String fileName) {
    return Path.of(workspaceRoot).resolve(fileName).toAbsolutePath().toString();
  }
}
