/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultCheckConnectionWorker implements CheckConnectionWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultCheckConnectionWorker.class);

  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;

  private Process process;

  public DefaultCheckConnectionWorker(final IntegrationLauncher integrationLauncher,
                                      final AirbyteStreamFactory streamFactory) {
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
  }

  public DefaultCheckConnectionWorker(final IntegrationLauncher integrationLauncher) {
    this(integrationLauncher, new DefaultAirbyteStreamFactory());
  }

  @Override
  public ConnectorJobOutput run(final StandardCheckConnectionInput input, final Path jobRoot) throws WorkerException {
    LineGobbler.startSection("CHECK");

    try {
      process = integrationLauncher.check(
          jobRoot,
          WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
          Jsons.serialize(input.getConnectionConfiguration()));

      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      final Map<Type, List<AirbyteMessage>> messagesByType;
      try (final InputStream stdout = process.getInputStream()) {
        messagesByType = streamFactory.create(IOs.newBufferedReader(stdout))
            .collect(Collectors.groupingBy(AirbyteMessage::getType));

        WorkerUtils.gentleClose(process, 1, TimeUnit.MINUTES);
      }

      final int exitCode = process.exitValue();
      final Optional<AirbyteConnectionStatus> status = messagesByType
          .getOrDefault(Type.CONNECTION_STATUS, new ArrayList<>()).stream()
          .map(AirbyteMessage::getConnectionStatus)
          .findFirst();

      if (status.isPresent() && exitCode == 0) {
        final StandardCheckConnectionOutput output = new StandardCheckConnectionOutput()
            .withStatus(Enums.convertTo(status.get().getStatus(), Status.class))
            .withMessage(status.get().getMessage());

        LOGGER.debug("Check connection job subprocess finished with exit code {}", exitCode);
        LOGGER.debug("Check connection job received output: {}", output);
        LineGobbler.endSection("CHECK");
        return new ConnectorJobOutput().withOutputType(OutputType.CHECK_CONNECTION).withCheckConnection(output);
      } else {
        final String message = String.format("Error checking connection, status: %s, exit code: %d", status, exitCode);
        LOGGER.error(message);

        return WorkerUtils.getJobFailureOutputOrThrow(OutputType.CHECK_CONNECTION, messagesByType, message);
      }

    } catch (final Exception e) {
      LOGGER.error("Unexpected error while checking connection: ", e);
      throw new WorkerException("Unexpected error while getting checking connection.", e);
    }
  }

  @Override
  public void cancel() {
    WorkerUtils.cancelProcess(process);
  }

}
