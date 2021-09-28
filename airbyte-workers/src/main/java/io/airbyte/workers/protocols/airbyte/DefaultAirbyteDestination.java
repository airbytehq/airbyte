/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import com.google.common.base.Charsets;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.file.Path;
import java.util.Iterator;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultAirbyteDestination implements AirbyteDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultAirbyteDestination.class);

  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;

  private final AtomicBoolean endOfStream = new AtomicBoolean(false);

  private Process destinationProcess = null;
  private BufferedWriter writer = null;
  private Iterator<AirbyteMessage> messageIterator = null;

  public DefaultAirbyteDestination(final IntegrationLauncher integrationLauncher) {
    this(integrationLauncher, new DefaultAirbyteStreamFactory());

  }

  public DefaultAirbyteDestination(final IntegrationLauncher integrationLauncher,
                                   final AirbyteStreamFactory streamFactory) {
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
  }

  @Override
  public void start(WorkerDestinationConfig destinationConfig, Path jobRoot) throws IOException, WorkerException {
    Preconditions.checkState(destinationProcess == null);

    LOGGER.info("Running destination...");
    destinationProcess = integrationLauncher.write(
        jobRoot,
        WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
        Jsons.serialize(destinationConfig.getDestinationConnectionConfiguration()),
        WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME,
        Jsons.serialize(destinationConfig.getCatalog()));
    // stdout logs are logged elsewhere since stdout also contains data
    LineGobbler.gobble(destinationProcess.getErrorStream(), LOGGER::error, "airbyte-destination");

    writer = new BufferedWriter(new OutputStreamWriter(destinationProcess.getOutputStream(), Charsets.UTF_8));

    messageIterator = streamFactory.create(IOs.newBufferedReader(destinationProcess.getInputStream()))
        .filter(message -> message.getType() == Type.STATE)
        .iterator();
  }

  @Override
  public void accept(AirbyteMessage message) throws IOException {
    Preconditions.checkState(destinationProcess != null && !endOfStream.get());

    writer.write(Jsons.serialize(message));
    writer.newLine();
  }

  @Override
  public void notifyEndOfStream() throws IOException {
    Preconditions.checkState(destinationProcess != null && !endOfStream.get());

    writer.flush();
    writer.close();
    endOfStream.set(true);
  }

  @Override
  public void close() throws Exception {
    if (destinationProcess == null) {
      LOGGER.debug("Destination process already exited");
      return;
    }

    if (!endOfStream.get()) {
      notifyEndOfStream();
    }

    LOGGER.debug("Closing destination process");
    WorkerUtils.gentleClose(destinationProcess, 10, TimeUnit.HOURS);
    if (destinationProcess.isAlive() || destinationProcess.exitValue() != 0) {
      String message =
          destinationProcess.isAlive() ? "Destination has not terminated " : "Destination process exit with code " + destinationProcess.exitValue();
      throw new WorkerException(message + ". This warning is normal if the job was cancelled.");
    }
  }

  @Override
  public void cancel() throws Exception {
    LOGGER.info("Attempting to cancel destination process...");

    if (destinationProcess == null) {
      LOGGER.info("Destination process no longer exists, cancellation is a no-op.");
    } else {
      LOGGER.info("Destination process exists, cancelling...");
      WorkerUtils.cancelProcess(destinationProcess);
      LOGGER.info("Cancelled destination process!");
    }
  }

  @Override
  public boolean isFinished() {
    Preconditions.checkState(destinationProcess != null);
    // As this check is done on every message read, it is important for this operation to be efficient.
    // Short circuit early to avoid checking the underlying process.
    var isEmpty = !messageIterator.hasNext();
    if (!isEmpty) {
      return false;
    }

    return !destinationProcess.isAlive();
  }

  @Override
  public Optional<AirbyteMessage> attemptRead() {
    Preconditions.checkState(destinationProcess != null);

    return Optional.ofNullable(messageIterator.hasNext() ? messageIterator.next() : null);
  }

}
