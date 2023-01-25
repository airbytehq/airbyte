/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.FailureReason;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.protocol.models.AirbyteControlConnectorConfigMessage;
import io.airbyte.protocol.models.AirbyteControlMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import io.airbyte.protocol.models.Config;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.helper.FailureHelper;
import io.airbyte.workers.helper.FailureHelper.ConnectorCommand;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// TODO:(Issue-4824): Figure out how to log Docker process information.
public class WorkerUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerUtils.class);

  public static void gentleClose(final Process process, final long timeout, final TimeUnit timeUnit) {

    if (process == null) {
      return;
    }

    if (process.info() != null) {
      process.info().commandLine().ifPresent(commandLine -> LOGGER.debug("Gently closing process {}", commandLine));
    }

    try {
      if (process.isAlive()) {
        process.waitFor(timeout, timeUnit);
      }
    } catch (final InterruptedException e) {
      LOGGER.error("Exception while while waiting for process to finish", e);
    }

    if (process.isAlive()) {
      closeProcess(process, Duration.of(1, ChronoUnit.MINUTES));
    }
  }

  public static void closeProcess(final Process process, final Duration lastChanceDuration) {
    if (process == null) {
      return;
    }
    try {
      process.destroy();
      process.waitFor(lastChanceDuration.toMillis(), TimeUnit.MILLISECONDS);
      if (process.isAlive()) {
        LOGGER.warn("Process is still alive after calling destroy. Attempting to destroy forcibly...");
        process.destroyForcibly();
      }
    } catch (final InterruptedException e) {
      LOGGER.error("Exception when closing process.", e);
    }
  }

  public static void wait(final Process process) {
    try {
      process.waitFor();
    } catch (final InterruptedException e) {
      LOGGER.error("Exception while while waiting for process to finish", e);
    }
  }

  public static void cancelProcess(final Process process) {
    closeProcess(process, Duration.of(10, ChronoUnit.SECONDS));
  }

  /**
   * Translates a StandardSyncInput into a WorkerSourceConfig. WorkerSourceConfig is a subset of
   * StandardSyncInput.
   */
  public static WorkerSourceConfig syncToWorkerSourceConfig(final StandardSyncInput sync) {
    return new WorkerSourceConfig()
        .withSourceId(sync.getSourceId())
        .withSourceConnectionConfiguration(sync.getSourceConfiguration())
        .withCatalog(sync.getCatalog())
        .withState(sync.getState());
  }

  /**
   * Translates a StandardSyncInput into a WorkerDestinationConfig. WorkerDestinationConfig is a
   * subset of StandardSyncInput.
   */
  public static WorkerDestinationConfig syncToWorkerDestinationConfig(final StandardSyncInput sync) {
    return new WorkerDestinationConfig()
        .withDestinationId(sync.getDestinationId())
        .withDestinationConnectionConfiguration(sync.getDestinationConfiguration())
        .withCatalog(sync.getCatalog())
        .withState(sync.getState());
  }

  private static ConnectorCommand getConnectorCommandFromOutputType(final OutputType outputType) {
    return switch (outputType) {
      case SPEC -> ConnectorCommand.SPEC;
      case CHECK_CONNECTION -> ConnectorCommand.CHECK;
      case DISCOVER_CATALOG_ID -> ConnectorCommand.DISCOVER;
    };
  }

  public static Optional<AirbyteControlConnectorConfigMessage> getMostRecentConfigControlMessage(final Map<Type, List<AirbyteMessage>> messagesByType) {
    return messagesByType.getOrDefault(Type.CONTROL, new ArrayList<>()).stream()
        .map(AirbyteMessage::getControl)
        .filter(control -> control.getType() == AirbyteControlMessage.Type.CONNECTOR_CONFIG)
        .map(AirbyteControlMessage::getConnectorConfig)
        .reduce((first, second) -> second);
  }

  private static Optional<AirbyteTraceMessage> getTraceMessageFromMessagesByType(final Map<Type, List<AirbyteMessage>> messagesByType) {
    return messagesByType.getOrDefault(Type.TRACE, new ArrayList<>()).stream()
        .map(AirbyteMessage::getTrace)
        .filter(trace -> trace.getType() == AirbyteTraceMessage.Type.ERROR)
        .findFirst();
  }

  public static Boolean getDidControlMessageChangeConfig(final JsonNode initialConfigJson, final AirbyteControlConnectorConfigMessage configMessage) {
    final Config newConfig = configMessage.getConfig();
    final JsonNode newConfigJson = Jsons.jsonNode(newConfig);
    return !initialConfigJson.equals(newConfigJson);
  }

  public static Map<Type, List<AirbyteMessage>> getMessagesByType(final Process process, final AirbyteStreamFactory streamFactory, final int timeOut)
      throws IOException {
    final Map<Type, List<AirbyteMessage>> messagesByType;
    try (final InputStream stdout = process.getInputStream()) {
      messagesByType = streamFactory.create(IOs.newBufferedReader(stdout))
          .collect(Collectors.groupingBy(AirbyteMessage::getType));

      WorkerUtils.gentleClose(process, timeOut, TimeUnit.MINUTES);
      return messagesByType;
    }
  }

  public static Optional<FailureReason> getJobFailureReasonFromMessages(final OutputType outputType,
                                                                        final Map<Type, List<AirbyteMessage>> messagesByType) {
    final Optional<AirbyteTraceMessage> traceMessage = getTraceMessageFromMessagesByType(messagesByType);
    if (traceMessage.isPresent()) {
      final ConnectorCommand connectorCommand = getConnectorCommandFromOutputType(outputType);
      return Optional.of(FailureHelper.connectorCommandFailure(traceMessage.get(), null, null, connectorCommand));
    } else {
      return Optional.empty();
    }

  }

  public static Map<AirbyteStreamNameNamespacePair, JsonNode> mapStreamNamesToSchemas(final StandardSyncInput syncInput) {
    return syncInput.getCatalog().getStreams().stream().collect(
        Collectors.toMap(
            k -> AirbyteStreamNameNamespacePair.fromAirbyteStream(k.getStream()),
            v -> v.getStream().getJsonSchema()));

  }

  public static String getStdErrFromErrorStream(final InputStream errorStream) throws IOException {
    final BufferedReader reader = new BufferedReader(new InputStreamReader(errorStream, StandardCharsets.UTF_8));
    final StringBuilder errorOutput = new StringBuilder();
    String line;
    while ((line = reader.readLine()) != null) {
      errorOutput.append(line);
      errorOutput.append(System.lineSeparator());
    }
    return errorOutput.toString();
  }

  public static void throwWorkerException(final String errorMessage, final Process process)
      throws WorkerException, IOException {
    final String stderr = getStdErrFromErrorStream(process.getErrorStream());
    if (stderr.isEmpty()) {
      throw new WorkerException(errorMessage);
    } else {
      throw new WorkerException(errorMessage + ": \n" + stderr);
    }
  }

}
