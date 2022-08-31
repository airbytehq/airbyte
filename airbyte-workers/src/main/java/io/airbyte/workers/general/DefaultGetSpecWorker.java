/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.WorkerConfigs;
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

public class DefaultGetSpecWorker implements GetSpecWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultGetSpecWorker.class);

  private final WorkerConfigs workerConfigs;
  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;

  private Process process;

  public DefaultGetSpecWorker(final WorkerConfigs workerConfigs,
                              final IntegrationLauncher integrationLauncher,
                              final AirbyteStreamFactory streamFactory) {
    this.workerConfigs = workerConfigs;
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
  }

  public DefaultGetSpecWorker(final WorkerConfigs workerConfigs, final IntegrationLauncher integrationLauncher) {
    this(workerConfigs, integrationLauncher, new DefaultAirbyteStreamFactory());
  }

  @Override
  public ConnectorJobOutput run(final JobGetSpecConfig config, final Path jobRoot) throws WorkerException {
    try {
      process = integrationLauncher.spec(jobRoot);

      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      final Map<Type, List<AirbyteMessage>> messagesByType;
      try (final InputStream stdout = process.getInputStream()) {
        messagesByType = streamFactory.create(IOs.newBufferedReader(stdout))
            .collect(Collectors.groupingBy(AirbyteMessage::getType));

        // todo (cgardens) - let's pre-fetch the images outside of the worker so we don't need account for
        // this.
        // retrieving spec should generally be instantaneous, but since docker images might not be pulled
        // it could take a while longer depending on internet conditions as well.
        WorkerUtils.gentleClose(workerConfigs, process, 30, TimeUnit.MINUTES);
      }

      final Optional<ConnectorSpecification> spec = messagesByType
          .getOrDefault(Type.SPEC, new ArrayList<>()).stream()
          .map(AirbyteMessage::getSpec)
          .findFirst();;

      final int exitCode = process.exitValue();
      if (exitCode == 0) {
        if (spec.isEmpty()) {
          throw new WorkerException("integration failed to output a spec struct.");
        }

        return new ConnectorJobOutput().withOutputType(OutputType.SPEC).withSpec(spec.get());
      } else {
        return WorkerUtils.getJobFailureOutputOrThrow(
            OutputType.SPEC,
            messagesByType,
            String.format("Spec job subprocess finished with exit code %s", exitCode));
      }
    } catch (final Exception e) {
      throw new WorkerException(String.format("Error while getting spec from image %s", config.getDockerImage()), e);
    }

  }

  @Override
  public void cancel() {
    WorkerUtils.cancelProcess(process);
  }

}
