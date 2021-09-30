/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.WorkerSourceConfig;
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

  private Process sourceProcess = null;
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
  public void start(WorkerSourceConfig sourceConfig, Path jobRoot) throws Exception {
    Preconditions.checkState(sourceProcess == null);

    sourceProcess = integrationLauncher.read(jobRoot,
        WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
        Jsons.serialize(sourceConfig.getSourceConnectionConfiguration()),
        WorkerConstants.SOURCE_CATALOG_JSON_FILENAME,
        Jsons.serialize(sourceConfig.getCatalog()),
        sourceConfig.getState() == null ? null : WorkerConstants.INPUT_STATE_JSON_FILENAME,
        sourceConfig.getState() == null ? null : Jsons.serialize(sourceConfig.getState().getState()));
    // stdout logs are logged elsewhere since stdout also contains data
    LineGobbler.gobble(sourceProcess.getErrorStream(), LOGGER::error, "airbyte-source");

    messageIterator = streamFactory.create(IOs.newBufferedReader(sourceProcess.getInputStream()))
        .peek(message -> heartbeatMonitor.beat())
        .filter(message -> message.getType() == Type.RECORD || message.getType() == Type.STATE)
        .iterator();
  }

  @Override
  public boolean isFinished() {
    Preconditions.checkState(sourceProcess != null);
    // As this check is done on every message read, it is important for this operation to be efficient.
    // Short circuit early to avoid checking the underlying process.
    var isEmpty = !messageIterator.hasNext();
    if (!isEmpty) {
      return false;
    }

    return !sourceProcess.isAlive() && !messageIterator.hasNext();
  }

  @Override
  public Optional<AirbyteMessage> attemptRead() {
    Preconditions.checkState(sourceProcess != null);

    return Optional.ofNullable(messageIterator.hasNext() ? messageIterator.next() : null);
  }

  @Override
  public void close() throws Exception {
    if (sourceProcess == null) {
      LOGGER.debug("Source process already exited");
      return;
    }

    LOGGER.debug("Closing source process");
    WorkerUtils.gentleCloseWithHeartbeat(
        sourceProcess,
        heartbeatMonitor,
        GRACEFUL_SHUTDOWN_DURATION,
        CHECK_HEARTBEAT_DURATION,
        FORCED_SHUTDOWN_DURATION);

    if (sourceProcess.isAlive() || sourceProcess.exitValue() != 0) {
      String message = sourceProcess.isAlive() ? "Source has not terminated " : "Source process exit with code " + sourceProcess.exitValue();
      throw new WorkerException(message + ". This warning is normal if the job was cancelled.");
    }
  }

  @Override
  public void cancel() throws Exception {
    LOGGER.info("Attempting to cancel source process...");

    if (sourceProcess == null) {
      LOGGER.info("Source process no longer exists, cancellation is a no-op.");
    } else {
      LOGGER.info("Source process exists, cancelling...");
      WorkerUtils.cancelProcess(sourceProcess);
      LOGGER.info("Cancelled source process!");
    }
  }

}
