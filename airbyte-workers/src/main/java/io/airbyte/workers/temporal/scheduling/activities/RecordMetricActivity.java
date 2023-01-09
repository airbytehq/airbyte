/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.commons.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.metrics.lib.MetricAttribute;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import java.util.Optional;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Custom Temporal activity that records metrics.
 */
@ActivityInterface
public interface RecordMetricActivity {

  enum FailureCause {
    ACTIVITY,
    CANCELED,
    CONNECTION,
    UNKNOWN,
    WORKFLOW
  }

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class RecordMetricInput {

    private ConnectionUpdaterInput connectionUpdaterInput;
    private Optional<FailureCause> failureCause;
    private OssMetricsRegistry metricName;
    private MetricAttribute[] metricAttributes;

  }

  /**
   * Records a counter metric.
   *
   * @param metricInput The metric information.
   */
  @ActivityMethod
  void recordWorkflowCountMetric(final RecordMetricInput metricInput);

}
