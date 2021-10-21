/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.commons.logging.LoggingHelper;
import io.airbyte.commons.logging.LoggingHelper.Color;
import io.airbyte.commons.logging.ScopedMDCChange;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.ResourceRequirements;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DbtTransformationWorker implements Worker<OperatorDbtInput, Void>, Application {

  private static final Logger LOGGER = LoggerFactory.getLogger(DbtTransformationWorker.class);

  private final String jobId;
  private final int attempt;
  private final DbtTransformationRunner dbtTransformationRunner;
  private final ResourceRequirements resourceRequirements;
  private final Map<String, String> newMDCValue;

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

    this.newMDCValue = new HashMap<>() {{
      put(LoggingHelper.LOG_SOURCE_MDC_KEY, LoggingHelper.applyColor(Color.GREEN, getApplicationName()));
    }};
  }

  @Override
  public Void run(final OperatorDbtInput operatorDbtInput, final Path jobRoot) throws WorkerException {
    try (final ScopedMDCChange scopedMDCChange = new ScopedMDCChange(newMDCValue)) {
      final long startTime = System.currentTimeMillis();

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
        throw new WorkerException("Dbt Transformation Failed.", e);
      }
      if (cancelled.get()) {
        LOGGER.info("Dbt Transformation was cancelled.");
      }

      final Duration duration = Duration.ofMillis(System.currentTimeMillis() - startTime);
      LOGGER.info("Dbt Transformation executed in {}.", duration.toMinutesPart());

      return null;
    } catch (final Exception e) {
      throw new WorkerException(getApplicationName() + " failed", e);
    }
  }

  @Override
  public void cancel() {
    try (final ScopedMDCChange scopedMDCChange = new ScopedMDCChange(newMDCValue)) {
      LOGGER.info("Cancelling Dbt Transformation runner...");
      try {
        cancelled.set(true);
        dbtTransformationRunner.close();
      } catch (final Exception e) {
        e.printStackTrace();
      }
    } catch (final Exception e) {
      e.printStackTrace();
    }
  }

  @Override public String getApplicationName() {
    return "airbyte-dbt-transformation-worker";
  }
}
