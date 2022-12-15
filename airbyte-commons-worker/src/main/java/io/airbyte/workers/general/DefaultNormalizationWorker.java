/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ROOT_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;

import datadog.trace.api.Trace;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.FailureReason;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.helper.FailureHelper;
import io.airbyte.workers.normalization.NormalizationRunner;
import io.airbyte.workers.normalization.NormalizationWorker;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
import org.apache.commons.lang3.time.DurationFormatUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("PMD.AvoidPrintStackTrace")
public class DefaultNormalizationWorker implements NormalizationWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultNormalizationWorker.class);

  private final String jobId;
  private final int attempt;
  private final NormalizationRunner normalizationRunner;
  private final WorkerEnvironment workerEnvironment;
  private final List<FailureReason> traceFailureReasons = new ArrayList<>();
  private boolean failed = false;

  private final AtomicBoolean cancelled;

  public DefaultNormalizationWorker(final String jobId,
                                    final int attempt,
                                    final NormalizationRunner normalizationRunner,
                                    final WorkerEnvironment workerEnvironment) {
    this.jobId = jobId;
    this.attempt = attempt;
    this.normalizationRunner = normalizationRunner;
    this.workerEnvironment = workerEnvironment;

    this.cancelled = new AtomicBoolean(false);
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public NormalizationSummary run(final NormalizationInput input, final Path jobRoot) throws WorkerException {
    final long startTime = System.currentTimeMillis();

    ApmTraceUtils.addTagsToTrace(Map.of(JOB_ID_KEY, jobId, JOB_ROOT_KEY, jobRoot));

    try (normalizationRunner) {
      LineGobbler.startSection("DEFAULT NORMALIZATION");
      normalizationRunner.start();

      Path normalizationRoot = null;
      // There are no shared volumes on Kube; only create this for Docker.
      if (workerEnvironment.equals(WorkerEnvironment.DOCKER)) {
        normalizationRoot = Files.createDirectories(jobRoot.resolve("normalize"));
      }

      if (!normalizationRunner.normalize(jobId, attempt, normalizationRoot, input.getDestinationConfiguration(), input.getCatalog(),
          input.getResourceRequirements())) {
        buildFailureReasonsAndSetFailure();
      }
    } catch (final Exception e) {
      ApmTraceUtils.addExceptionToTrace(e);
      LOGGER.error("Normalization failed for job {}.", jobId, e);
      buildFailureReasonsAndSetFailure();
    }

    if (cancelled.get()) {
      LOGGER.info("Normalization was cancelled for job {}.", jobId);
    }

    final long endTime = System.currentTimeMillis();
    final Duration duration = Duration.ofMillis(endTime - startTime);
    final String durationDescription = DurationFormatUtils.formatDurationWords(duration.toMillis(), true, true);
    LOGGER.info("Normalization executed in {} for job {}.", durationDescription, jobId);

    final NormalizationSummary summary = new NormalizationSummary()
        .withStartTime(startTime)
        .withEndTime(endTime);

    if (!traceFailureReasons.isEmpty()) {
      summary.setFailures(traceFailureReasons);
    } else if (failed) {
      throw new WorkerException("Normalization Failed.");
    }

    LOGGER.info("Normalization summary: {}", summary);
    LineGobbler.endSection("DEFAULT NORMALIZATION");

    return summary;
  }

  private void buildFailureReasonsAndSetFailure() {
    normalizationRunner.getTraceMessages()
        .filter(traceMessage -> traceMessage.getType() == AirbyteTraceMessage.Type.ERROR)
        .forEach(traceMessage -> traceFailureReasons.add(FailureHelper.normalizationFailure(traceMessage, Long.valueOf(jobId), attempt)));
    failed = true;
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void cancel() {
    LOGGER.info("Cancelling normalization runner...");
    try {
      cancelled.set(true);
      normalizationRunner.close();
    } catch (final Exception e) {
      ApmTraceUtils.addExceptionToTrace(e);
      LOGGER.error("Unable to cancel normalization runner.", e);
    }
  }

}
