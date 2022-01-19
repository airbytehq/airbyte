/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.protocols.airbyte.AirbyteStreamFactory;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteStreamFactory;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultCheckConnectionWorker implements CheckConnectionWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultCheckConnectionWorker.class);

  private final WorkerConfigs workerConfigs;
  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;

  private Process process;

  public DefaultCheckConnectionWorker(final WorkerConfigs workerConfigs,
                                      final IntegrationLauncher integrationLauncher,
                                      final AirbyteStreamFactory streamFactory) {
    this.workerConfigs = workerConfigs;
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
  }

  public DefaultCheckConnectionWorker(final WorkerConfigs workerConfigs, final IntegrationLauncher integrationLauncher) {
    this(workerConfigs, integrationLauncher, new DefaultAirbyteStreamFactory());
  }

  @Override
  public StandardCheckConnectionOutput run(final StandardCheckConnectionInput input, final Path jobRoot) throws WorkerException {

    try {
      process = integrationLauncher.check(
          jobRoot,
          WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
          Jsons.serialize(input.getConnectionConfiguration()));

      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      final Optional<AirbyteConnectionStatus> status;
      try (final InputStream stdout = process.getInputStream()) {
        status = streamFactory.create(IOs.newBufferedReader(stdout))
            .filter(message -> message.getType() == Type.CONNECTION_STATUS)
            .map(AirbyteMessage::getConnectionStatus).findFirst();

        WorkerUtils.gentleClose(workerConfigs, process, 1, TimeUnit.MINUTES);
      }

      final int exitCode = process.exitValue();

      if (status.isPresent() && exitCode == 0) {
        final StandardCheckConnectionOutput output = new StandardCheckConnectionOutput()
            .withStatus(Enums.convertTo(status.get().getStatus(), Status.class))
            .withMessage(status.get().getMessage());

        LOGGER.debug("Check connection job subprocess finished with exit code {}", exitCode);
        LOGGER.debug("Check connection job received output: {}", output);
        return output;
      } else {
        throw new WorkerException(String.format("Error checking connection, status: %s, exit code: %d", status, exitCode));
      }

    } catch (final Exception e) {
      throw new WorkerException("Error while getting checking connection.", e);
    }
  }

  @Override
  public void cancel() {
    WorkerUtils.cancelProcess(process);
  }

}
