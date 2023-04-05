/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.commons.io.LineGobbler;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.FailureReason;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.TestHarnessUtils;
import io.airbyte.workers.exception.TestHarnessException;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultGetSpecTestHarness implements GetSpecTestHarness {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultGetSpecTestHarness.class);

  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;
  private Process process;

  public DefaultGetSpecTestHarness(final IntegrationLauncher integrationLauncher,
                                   final AirbyteStreamFactory streamFactory) {
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
  }

  public DefaultGetSpecTestHarness(final IntegrationLauncher integrationLauncher) {
    this(integrationLauncher, new DefaultAirbyteStreamFactory());
  }

  @Override
  public ConnectorJobOutput run(final JobGetSpecConfig config, final Path jobRoot) throws TestHarnessException {
    try {
      process = integrationLauncher.spec(jobRoot);

      final ConnectorJobOutput jobOutput = new ConnectorJobOutput().withOutputType(OutputType.SPEC);
      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      final Map<Type, List<AirbyteMessage>> messagesByType = TestHarnessUtils.getMessagesByType(process, streamFactory, 30);

      final Optional<ConnectorSpecification> spec = messagesByType
          .getOrDefault(Type.SPEC, new ArrayList<>()).stream()
          .map(AirbyteMessage::getSpec)
          .findFirst();

      final Optional<FailureReason> failureReason = TestHarnessUtils.getJobFailureReasonFromMessages(OutputType.SPEC, messagesByType);
      failureReason.ifPresent(jobOutput::setFailureReason);

      final int exitCode = process.exitValue();
      if (exitCode != 0) {
        LOGGER.warn("Spec job subprocess finished with exit code {}", exitCode);
      }

      if (spec.isPresent()) {
        jobOutput.setSpec(spec.get());
      } else if (failureReason.isEmpty()) {
        TestHarnessUtils.throwWorkerException("Integration failed to output a spec struct and did not output a failure reason", process);
      }

      return jobOutput;
    } catch (final Exception e) {
      throw new TestHarnessException(String.format("Error while getting spec from image %s", config.getDockerImage()), e);
    }

  }

  @Override
  public void cancel() {
    TestHarnessUtils.cancelProcess(process);
  }

}
