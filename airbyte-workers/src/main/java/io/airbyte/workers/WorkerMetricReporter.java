/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.metrics.lib.MetricAttribute;
import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.OssMetricsRegistry;

public class WorkerMetricReporter {

  private final String dockerRepo;
  private final String dockerVersion;
  private final MetricClient metricClient;

  public WorkerMetricReporter(final MetricClient metricClient, final String dockerImage) {
    final String[] dockerImageInfo = dockerImage.split(":");
    this.dockerRepo = dockerImageInfo[0];
    this.dockerVersion = dockerImageInfo.length > 1 ? dockerImageInfo[1] : "";
    this.metricClient = metricClient;
  }

  public void trackSchemaValidationError(final String stream) {
    metricClient.count(OssMetricsRegistry.NUM_SOURCE_STREAMS_WITH_RECORD_SCHEMA_VALIDATION_ERRORS, 1, new MetricAttribute("docker_repo", dockerRepo),
        new MetricAttribute("docker_version", dockerVersion), new MetricAttribute("stream", stream));
  }

}
