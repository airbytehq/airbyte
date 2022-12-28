/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.DOCKER_IMAGE_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ROOT_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;

import datadog.trace.api.Trace;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.protocol.objects.ConnectorSpecification;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.ConnectorJobOutput.OutputType;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.internal.AirbyteMessageReader;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
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

      LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

      final AirbyteMessageReader messageReader;
      try (final InputStream stdout = process.getInputStream()) {
        messageReader = new AirbyteMessageReader(streamFactory.create(IOs.newBufferedReader(stdout)));

        // todo (cgardens) - let's pre-fetch the images outside of the worker so we don't need account for
        // this.
        // retrieving spec should generally be instantaneous, but since docker images might not be pulled
        // it could take a while longer depending on internet conditions as well.
        WorkerUtils.gentleClose(process, 30, TimeUnit.MINUTES);
      }

      final Optional<ConnectorSpecification> spec = messageReader.getSpecs().findFirst();

      final int exitCode = process.exitValue();
      if (exitCode == 0) {
        if (spec.isEmpty()) {
          throw new WorkerException("integration failed to output a spec struct.");
        }

        return new ConnectorJobOutput().withOutputType(OutputType.SPEC).withSpec(spec.get());
      } else {
        return WorkerUtils.getJobFailureOutputOrThrow(
            OutputType.SPEC,
            messageReader.getTraces(),
            String.format("Spec job subprocess finished with exit code %s", exitCode));
      }
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
