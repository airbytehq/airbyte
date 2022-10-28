/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ROOT_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;

import datadog.trace.api.Trace;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.workers.Worker;
import io.airbyte.workers.exception.WorkerException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("PMD.AvoidPrintStackTrace")
public class DbtTransformationWorker implements Worker<OperatorDbtInput, Void> {

  private static final Logger LOGGER = LoggerFactory.getLogger(DbtTransformationWorker.class);

  private final String jobId;
  private final int attempt;
  private final DbtTransformationRunner dbtTransformationRunner;
  private final ResourceRequirements resourceRequirements;

  private final AtomicBoolean cancelled;

  public DbtTransformationWorker(final String jobId,
                                 final int attempt,
                                 final ResourceRequirements resourceRequirements,
                                 final DbtTransformationRunner dbtTransformationRunner) {
    this.jobId = jobId;
    this.attempt = attempt;
    this.dbtTransformationRunner = dbtTransformationRunner;
    this.resourceRequirements = resourceRequirements;

    this.cancelled = new AtomicBoolean(false);
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public Void run(final OperatorDbtInput operatorDbtInput, final Path jobRoot) throws WorkerException {
    final long startTime = System.currentTimeMillis();
    LineGobbler.startSection("DBT TRANSFORMATION");
    ApmTraceUtils.addTagsToTrace(Map.of(JOB_ID_KEY, jobId, JOB_ROOT_KEY, jobRoot));

    try (dbtTransformationRunner) {
      LOGGER.info("Running dbt transformation.");
      dbtTransformationRunner.start();
      final Path transformRoot = Files.createDirectories(jobRoot.resolve("transform"));
      if (!dbtTransformationRunner.run(
          jobId,
          attempt,
          transformRoot,
          operatorDbtInput.getDestinationConfiguration(),
          resourceRequirements,
          operatorDbtInput.getOperatorDbt())) {
        throw new WorkerException("DBT Transformation Failed.");
      }
    } catch (final Exception e) {
      ApmTraceUtils.addExceptionToTrace(e);
      throw new WorkerException("Dbt Transformation Failed.", e);
    }
    if (cancelled.get()) {
      LOGGER.info("Dbt Transformation was cancelled.");
    }

    final Duration duration = Duration.ofMillis(System.currentTimeMillis() - startTime);
    LOGGER.info("Dbt Transformation executed in {}.", duration.toMinutesPart());
    LineGobbler.endSection("DBT TRANSFORMATION");

    return null;
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void cancel() {
    LOGGER.info("Cancelling Dbt Transformation runner...");
    try {
      cancelled.set(true);
      dbtTransformationRunner.close();
    } catch (final Exception e) {
      ApmTraceUtils.addExceptionToTrace(e);
      LOGGER.error("Unable to cancel Dbt Transformation runner.", e);
    }
  }

}
