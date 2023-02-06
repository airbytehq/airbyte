/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;

import com.google.common.base.Charsets;
import com.google.common.base.Preconditions;
import datadog.trace.api.Trace;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.LoggingHelper.Color;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.commons.logging.MdcScope.Builder;
import io.airbyte.commons.protocol.DefaultProtocolSerializer;
import io.airbyte.commons.protocol.ProtocolSerializer;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.nio.file.Path;
import java.util.Iterator;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultAirbyteDestination implements AirbyteDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultAirbyteDestination.class);
  public static final MdcScope.Builder CONTAINER_LOG_MDC_BUILDER = new Builder()
      .setLogPrefix("destination")
      .setPrefixColor(Color.YELLOW_BACKGROUND);
  static final Set<Integer> IGNORED_EXIT_CODES = Set.of(
      0, // Normal exit
      143 // SIGTERM
  );

  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;
  private final AirbyteMessageBufferedWriterFactory messageWriterFactory;
  private final ProtocolSerializer protocolSerializer;

  private final AtomicBoolean inputHasEnded = new AtomicBoolean(false);

  private Process destinationProcess = null;
  private AirbyteMessageBufferedWriter writer = null;
  private Iterator<AirbyteMessage> messageIterator = null;
  private Integer exitValue = null;

  public DefaultAirbyteDestination(final IntegrationLauncher integrationLauncher) {
    this(integrationLauncher, new DefaultAirbyteStreamFactory(CONTAINER_LOG_MDC_BUILDER), new DefaultAirbyteMessageBufferedWriterFactory(),
        new DefaultProtocolSerializer());

  }

  public DefaultAirbyteDestination(final IntegrationLauncher integrationLauncher,
                                   final AirbyteStreamFactory streamFactory,
                                   final AirbyteMessageBufferedWriterFactory messageWriterFactory,
                                   final ProtocolSerializer protocolSerializer) {
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
    this.messageWriterFactory = messageWriterFactory;
    this.protocolSerializer = protocolSerializer;
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void start(final WorkerDestinationConfig destinationConfig, final Path jobRoot) throws IOException, WorkerException {
    Preconditions.checkState(destinationProcess == null);

    LOGGER.info("Running destination...");
    destinationProcess = integrationLauncher.write(
        jobRoot,
        WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
        Jsons.serialize(destinationConfig.getDestinationConnectionConfiguration()),
        WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME,
        protocolSerializer.serialize(destinationConfig.getCatalog()));
    // stdout logs are logged elsewhere since stdout also contains data
    LineGobbler.gobble(destinationProcess.getErrorStream(), LOGGER::error, "airbyte-destination", CONTAINER_LOG_MDC_BUILDER);

    writer = messageWriterFactory.createWriter(new BufferedWriter(new OutputStreamWriter(destinationProcess.getOutputStream(), Charsets.UTF_8)));

    final List<Type> acceptedMessageTypes = List.of(Type.STATE, Type.TRACE, Type.CONTROL);
    messageIterator = streamFactory.create(IOs.newBufferedReader(destinationProcess.getInputStream()))
        .filter(message -> acceptedMessageTypes.contains(message.getType()))
        .iterator();
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void accept(final AirbyteMessage message) throws IOException {
    Preconditions.checkState(destinationProcess != null && !inputHasEnded.get());

    writer.write(message);
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void notifyEndOfInput() throws IOException {
    Preconditions.checkState(destinationProcess != null && !inputHasEnded.get());

    writer.flush();
    writer.close();
    inputHasEnded.set(true);
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void close() throws Exception {
    if (destinationProcess == null) {
      LOGGER.debug("Destination process already exited");
      return;
    }

    if (!inputHasEnded.get()) {
      notifyEndOfInput();
    }

    LOGGER.debug("Closing destination process");
    WorkerUtils.gentleClose(destinationProcess, 1, TimeUnit.MINUTES);
    if (destinationProcess.isAlive() || !IGNORED_EXIT_CODES.contains(getExitValue())) {
      final String message =
          destinationProcess.isAlive() ? "Destination has not terminated " : "Destination process exit with code " + getExitValue();
      throw new WorkerException(message + ". This warning is normal if the job was cancelled.");
    }
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
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

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public boolean isFinished() {
    Preconditions.checkState(destinationProcess != null);
    /*
     * As this check is done on every message read, it is important for this operation to be efficient.
     * Short circuit early to avoid checking the underlying process. Note: hasNext is blocking.
     */
    return !messageIterator.hasNext() && !destinationProcess.isAlive();
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public int getExitValue() {
    Preconditions.checkState(destinationProcess != null, "Destination process is null, cannot retrieve exit value.");
    Preconditions.checkState(!destinationProcess.isAlive(), "Destination process is still alive, cannot retrieve exit value.");

    if (exitValue == null) {
      exitValue = destinationProcess.exitValue();
    }

    return exitValue;
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public Optional<AirbyteMessage> attemptRead() {
    Preconditions.checkState(destinationProcess != null);

    return Optional.ofNullable(messageIterator.hasNext() ? messageIterator.next() : null);
  }

}
