/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import io.airbyte.workers.general.DefaultReplicationWorker;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class WorkerMetricReporter {

  private final String dockerRepo;
  private final String dockerVersion;
  private final MetricClient metricClient;
  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerMetricReporter.class);

  public WorkerMetricReporter(final MetricClient metricClient, final String dockerImage) {
    final String[] dockerImageInfo = dockerImage.split(":");
    this.dockerRepo = dockerImageInfo[0];
    this.dockerVersion = dockerImageInfo.length > 1 ? dockerImageInfo[1] : "";
    this.metricClient = metricClient;
  }

  public void trackSchemaValidationError(final String stream) {
    final String[] validationErrorMetadata = {
      "docker_repo:" + dockerRepo,
      "docker_version:" + dockerVersion,
      "stream:" + stream
    };
    LOGGER.info("tracking record schema validation error");
    metricClient.count(OssMetricsRegistry.NUM_SOURCE_STREAMS_WITH_RECORD_SCHEMA_VALIDATION_ERRORS, 1, validationErrorMetadata);
  }

}
