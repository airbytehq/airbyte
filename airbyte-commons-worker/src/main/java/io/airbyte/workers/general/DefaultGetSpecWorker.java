/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.DOCKER_IMAGE_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ROOT_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;

import datadog.trace.api.Trace;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.FailureReason;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
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

public class DefaultGetSpecWorker implements GetSpecWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultGetSpecWorker.class);

  private final IntegrationLauncher integrationLauncher;
  private final AirbyteStreamFactory streamFactory;
  private Process process;

  public DefaultGetSpecWorker(final IntegrationLauncher integrationLauncher,
                              final AirbyteStreamFactory streamFactory) {
    this.integrationLauncher = integrationLauncher;
    this.streamFactory = streamFactory;
  }

  public DefaultGetSpecWorker(final IntegrationLauncher integrationLauncher) {
    this(integrationLauncher, new DefaultAirbyteStreamFactory());
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public ConnectorJobOutput run(final JobGetSpecConfig config, final Path jobRoot) throws WorkerException {
    ApmTraceUtils.addTagsToTrace(Map.of(JOB_ROOT_KEY, jobRoot, DOCKER_IMAGE_KEY, config.getDockerImage()));
    try {
      process = integrationLauncher.spec(jobRoot);

      final ConnectorJobOutput jobOutput = new ConnectorJobOutput().withOutputType(OutputType.SPEC);
      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      final Map<Type, List<AirbyteMessage>> messagesByType = WorkerUtils.getMessagesByType(process, streamFactory, 30);

      final Optional<ConnectorSpecification> spec = messagesByType
          .getOrDefault(Type.SPEC, new ArrayList<>()).stream()
          .map(AirbyteMessage::getSpec)
          .findFirst();

      final Optional<FailureReason> failureReason = WorkerUtils.getJobFailureReasonFromMessages(OutputType.SPEC, messagesByType);
      failureReason.ifPresent(jobOutput::setFailureReason);

      final int exitCode = process.exitValue();
      if (exitCode != 0) {
        LOGGER.warn("Spec job subprocess finished with exit code {}", exitCode);
      }

      if (spec.isPresent()) {
        jobOutput.setSpec(spec.get());
      } else if (failureReason.isEmpty()) {
        WorkerUtils.throwWorkerException("Integration failed to output a spec struct and did not output a failure reason", process);
      }

      return jobOutput;
    } catch (final Exception e) {
      throw new WorkerException(String.format("Error while getting spec from image %s", config.getDockerImage()), e);
    }

  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void cancel() {
    WorkerUtils.cancelProcess(process);
  }

}
