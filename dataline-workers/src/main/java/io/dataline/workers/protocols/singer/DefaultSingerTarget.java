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
import com.google.common.base.Charsets;
import com.google.common.base.Preconditions;
import io.dataline.commons.io.IOs;
import io.dataline.commons.json.Jsons;
import io.dataline.config.StandardTargetConfig;
import io.dataline.singer.SingerMessage;
import io.dataline.workers.WorkerUtils;
import io.dataline.workers.process.ProcessBuilderFactory;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSingerTarget implements SingerTarget {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSingerTarget.class);

  @VisibleForTesting
  static final String CONFIG_JSON_FILENAME = "target_config.json";

  private final String imageName;
  private final ProcessBuilderFactory pbf;

  private Process targetProcess;
  private BufferedWriter writer;

  public DefaultSingerTarget(final String imageName, final ProcessBuilderFactory pbf) {
    this.imageName = imageName;
    this.pbf = pbf;
  }

  @Override
  public void start(StandardTargetConfig targetConfig, Path jobRoot) {
    Preconditions.checkState(targetProcess == null);

    final JsonNode configDotJson = targetConfig.getDestinationConnectionImplementation().getConfiguration();

    // write config.json to disk
    IOs.writeFile(jobRoot, CONFIG_JSON_FILENAME, Jsons.serialize(configDotJson));

    try {
      LOGGER.info("Running Singer target...");
      targetProcess =
          pbf.create(jobRoot, imageName, "--config", CONFIG_JSON_FILENAME)
              .redirectError(jobRoot.resolve(SingerSyncWorker.TARGET_ERR_LOG).toFile())
              .redirectOutput(jobRoot.resolve(SingerSyncWorker.TARGET_ERR_LOG).toFile())
              .start();

      writer = new BufferedWriter(new OutputStreamWriter(targetProcess.getOutputStream(), Charsets.UTF_8));
    } catch (Exception e) {
      // TODO: we should probably do some cleanup here.
      throw new RuntimeException(e);
    }
  }

  @Override
  public void accept(SingerMessage message) throws IOException {
    Preconditions.checkState(targetProcess != null);

    writer.write(Jsons.serialize(message));
    writer.newLine();
  }

  @Override public void notifyEndOfStream() throws IOException {
    Preconditions.checkState(targetProcess != null);

    writer.flush();
    writer.close();
  }

  @Override
  public void close() throws Exception {
    if (targetProcess == null) {
      return;
    }

    LOGGER.debug("Closing target process");
    WorkerUtils.gentleClose(targetProcess, 1, TimeUnit.MINUTES);
    if (targetProcess.isAlive() || targetProcess.exitValue() != 0) {
      throw new Exception("target process wasn't successful");
    }
  }
}
