/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.NormalizationInput;
import io.airbyte.workers.normalization.NormalizationRunner;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.concurrent.atomic.AtomicBoolean;
import org.apache.commons.lang3.time.DurationFormatUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultNormalizationWorker implements NormalizationWorker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultNormalizationWorker.class);

  private final String jobId;
  private final int attempt;
  private final NormalizationRunner normalizationRunner;
  private final WorkerEnvironment workerEnvironment;

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

  @Override
  public Void run(final NormalizationInput input, final Path jobRoot) throws WorkerException {
    final long startTime = System.currentTimeMillis();

    try (normalizationRunner) {
      LOGGER.info("Running normalization.");
      normalizationRunner.start();

      Path normalizationRoot = null;
      // There are no shared volumes on Kube; only create this for Docker.
      if (workerEnvironment.equals(WorkerEnvironment.DOCKER)) {
        normalizationRoot = Files.createDirectories(jobRoot.resolve("normalize"));
      }

      if (!normalizationRunner.normalize(jobId, attempt, normalizationRoot, input.getDestinationConfiguration(), input.getCatalog(),
          input.getResourceRequirements())) {
        throw new WorkerException("Normalization Failed.");
      }
    } catch (final Exception e) {
      throw new WorkerException("Normalization Failed.", e);
    }

    if (cancelled.get()) {
      LOGGER.info("Normalization was cancelled.");
    }

    final Duration duration = Duration.ofMillis(System.currentTimeMillis() - startTime);
    final String durationDescription = DurationFormatUtils.formatDurationWords(duration.toMillis(), true, true);
    LOGGER.info("Normalization executed in {}.", durationDescription);

    return null;
  }

  @Override
  public void cancel() {
    LOGGER.info("Cancelling normalization runner...");
    try {
      cancelled.set(true);
      normalizationRunner.close();
    } catch (final Exception e) {
      e.printStackTrace();
    }
  }

}
