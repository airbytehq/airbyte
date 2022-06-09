package io.airbyte.workers;

import io.airbyte.metrics.lib.DatadogClientConfiguration;
import io.airbyte.metrics.lib.DogStatsDMetricSingleton;
import io.airbyte.metrics.lib.OssMetricsRegistry;

public class DatadogSchemaValidationMetricReporter {
  private final String dockerRepo;
  private final String dockerVersion;

  public DatadogSchemaValidationMetricReporter(final DatadogClientConfiguration ddConfig, final String dockerImage) {
    final String[] dockerImageInfo = dockerImage.split(":");
    this.dockerRepo = dockerImageInfo[0];
    this.dockerVersion = dockerImageInfo.length > 1 ? dockerImageInfo[1] : "";
  }

  public void track(final String stream) {
    final String[] validationErrorMetadata = {
        "docker_repo:" + dockerRepo,
        "docker_version:" + dockerVersion,
        "stream:" + stream
    };
    DogStatsDMetricSingleton.count(OssMetricsRegistry.NUM_RECORD_SCHEMA_VALIDATION_ERRORS, 1, validationErrorMetadata);
  }
}
