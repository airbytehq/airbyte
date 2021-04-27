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

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.IntegrationLauncher;
import java.nio.file.Path;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.Iterator;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultAirbyteSource implements AirbyteSource {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultAirbyteSource.class);

  private static final Duration HEARTBEAT_FRESH_DURATION = Duration.of(5, ChronoUnit.MINUTES);
  private static final Duration CHECK_HEARTBEAT_DURATION = Duration.of(10, ChronoUnit.SECONDS);
  // todo (cgardens) - keep the graceful shutdown consistent with current behavior for release. make
  // sure everything is working well before we reduce this to something more reasonable.
  private static final Duration GRACEFUL_SHUTDOWN_DURATION = Duration.of(10, ChronoUnit.HOURS);
  private static final Duration FORCED_SHUTDOWN_DURATION = Duration.of(1, ChronoUnit.MINUTES);

  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;
  private final HeartbeatMonitor heartbeatMonitor;

  private Process tapProcess = null;
  private Iterator<AirbyteMessage> messageIterator = null;

  public DefaultAirbyteSource(final IntegrationLauncher integrationLauncher) {
    this(integrationLauncher, new DefaultAirbyteStreamFactory(), new HeartbeatMonitor(HEARTBEAT_FRESH_DURATION));
  }

  @VisibleForTesting
  DefaultAirbyteSource(final IntegrationLauncher integrationLauncher,
                       final AirbyteStreamFactory streamFactory,
                       final HeartbeatMonitor heartbeatMonitor) {
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
    this.heartbeatMonitor = heartbeatMonitor;
  }

  @Override
  public void start(StandardTapConfig input, Path jobRoot) throws Exception {
    Preconditions.checkState(tapProcess == null);

    IOs.writeFile(jobRoot, WorkerConstants.SOURCE_CONFIG_JSON_FILENAME, Jsons.serialize(input.getSourceConnectionConfiguration()));
    IOs.writeFile(jobRoot, WorkerConstants.SOURCE_CATALOG_JSON_FILENAME, Jsons.serialize(input.getCatalog()));
    if (input.getState() != null) {
      IOs.writeFile(jobRoot, WorkerConstants.INPUT_STATE_JSON_FILENAME, Jsons.serialize(input.getState().getState()));
    }

    tapProcess = integrationLauncher.read(jobRoot,
        WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
        WorkerConstants.SOURCE_CATALOG_JSON_FILENAME,
        input.getState() == null ? null : WorkerConstants.INPUT_STATE_JSON_FILENAME).start();
    // stdout logs are logged elsewhere since stdout also contains data
    LineGobbler.gobble(tapProcess.getErrorStream(), LOGGER::error);

    messageIterator = streamFactory.create(IOs.newBufferedReader(tapProcess.getInputStream()))
        .peek(message -> heartbeatMonitor.beat())
        .filter(message -> message.getType() == Type.RECORD || message.getType() == Type.STATE)
        .iterator();
  }

  @Override
  public boolean isFinished() {
    Preconditions.checkState(tapProcess != null);

    return !tapProcess.isAlive() && !messageIterator.hasNext();
  }

  @Override
  public Optional<AirbyteMessage> attemptRead() {
    Preconditions.checkState(tapProcess != null);

    return Optional.ofNullable(messageIterator.hasNext() ? messageIterator.next() : null);
  }

  @Override
  public void close() throws Exception {
    if (tapProcess == null) {
      return;
    }

    LOGGER.debug("Closing tap process");
    WorkerUtils.gentleCloseWithHeartbeat(
        tapProcess,
        heartbeatMonitor,
        GRACEFUL_SHUTDOWN_DURATION,
        CHECK_HEARTBEAT_DURATION,
        FORCED_SHUTDOWN_DURATION);

    if (tapProcess.isAlive() || tapProcess.exitValue() != 0) {
      throw new WorkerException("Tap process wasn't successful");
    }
  }

  @Override
  public void cancel() throws Exception {
    LOGGER.info("Attempting to cancel source process...");

    if (tapProcess == null) {
      LOGGER.info("Source process no longer exists, cancellation is a no-op.");
    } else {
      LOGGER.info("Source process exists, cancelling...");
      WorkerUtils.cancelProcess(tapProcess);
      LOGGER.info("Cancelled source process!");
    }
  }

}
