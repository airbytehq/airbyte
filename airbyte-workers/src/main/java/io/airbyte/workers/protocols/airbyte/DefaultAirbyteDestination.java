/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
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

package io.airbyte.workers.protocols.airbyte;

import com.google.common.base.Charsets;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultAirbyteDestination implements AirbyteDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultAirbyteDestination.class);

  private final IntegrationLauncher integrationLauncher;

  private Process targetProcess = null;
  private BufferedWriter writer = null;
  private boolean endOfStream = false;

  public DefaultAirbyteDestination(final IntegrationLauncher integrationLauncher) {
    this.integrationLauncher = integrationLauncher;
  }

  @Override
  public void start(StandardTargetConfig targetConfig, Path jobRoot) throws IOException, WorkerException {
    Preconditions.checkState(targetProcess == null);

    IOs.writeFile(jobRoot, WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME, Jsons.serialize(targetConfig.getDestinationConnectionConfiguration()));
    IOs.writeFile(jobRoot, WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME, Jsons.serialize(targetConfig.getCatalog()));

    LOGGER.info("Running target...");
    targetProcess = integrationLauncher.write(
        jobRoot,
        WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
        WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME).start();
    LineGobbler.gobble(targetProcess.getInputStream(), LOGGER::info);
    LineGobbler.gobble(targetProcess.getErrorStream(), LOGGER::error);

    writer = new BufferedWriter(new OutputStreamWriter(targetProcess.getOutputStream(), Charsets.UTF_8));
  }

  @Override
  public void accept(AirbyteMessage message) throws IOException {
    Preconditions.checkState(targetProcess != null && !endOfStream);

    writer.write(Jsons.serialize(message));
    writer.newLine();
  }

  @Override
  public void notifyEndOfStream() throws IOException {
    Preconditions.checkState(targetProcess != null && !endOfStream);

    writer.flush();
    writer.close();
    endOfStream = true;
  }

  @Override
  public void close() throws WorkerException, IOException {
    if (targetProcess == null) {
      return;
    }

    if (!endOfStream) {
      notifyEndOfStream();
    }

    LOGGER.debug("Closing target process");
    WorkerUtils.gentleClose(targetProcess, 10, TimeUnit.HOURS);
    if (targetProcess.isAlive() || targetProcess.exitValue() != 0) {
      throw new WorkerException("target process wasn't successful");
    }
  }

  @Override
  public void cancel() throws Exception {
    LOGGER.info("Attempting to cancel destination process...");

    if (targetProcess == null) {
      LOGGER.info("Target process no longer exists, cancellation is a no-op.");
    } else {
      LOGGER.info("Target process exists, cancelling...");
      WorkerUtils.cancelProcess(targetProcess);
      LOGGER.info("Cancelled destination process!");
    }
  }

}
