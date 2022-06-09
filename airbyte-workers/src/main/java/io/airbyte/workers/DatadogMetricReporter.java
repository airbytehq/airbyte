/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.metrics.lib.DatadogClientConfiguration;
import io.airbyte.metrics.lib.DogStatsDMetricSingleton;
import io.airbyte.metrics.lib.OssMetricsRegistry;

public class DatadogMetricReporter {

  private final String dockerRepo;
  private final String dockerVersion;

  public DatadogMetricReporter(final DatadogClientConfiguration ddConfig, final String dockerImage) {
    final String[] dockerImageInfo = dockerImage.split(":");
    this.dockerRepo = dockerImageInfo[0];
    this.dockerVersion = dockerImageInfo.length > 1 ? dockerImageInfo[1] : "";
  }

  public void trackSchemaValidationError(final String stream) {
    final String[] validationErrorMetadata = {
      "docker_repo:" + dockerRepo,
      "docker_version:" + dockerVersion,
      "stream:" + stream
    };
    DogStatsDMetricSingleton.count(OssMetricsRegistry.NUM_RECORD_SCHEMA_VALIDATION_ERRORS, 1, validationErrorMetadata);
  }

}
