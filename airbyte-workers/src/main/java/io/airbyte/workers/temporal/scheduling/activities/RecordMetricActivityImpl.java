/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.metrics.lib.MetricAttribute;
import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.workers.temporal.scheduling.ConnectionUpdaterInput;
import io.micronaut.context.annotation.Requires;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.inject.Inject;
import javax.inject.Singleton;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;

/**
 * Implementation of the {@link RecordMetricActivity} that is managed by the application framework
 * and therefore has access to other singletons managed by the framework.
 */
@AllArgsConstructor
@NoArgsConstructor
@Slf4j
@Singleton
@Requires(property = "airbyte.worker.plane",
          pattern = "(?i)^(?!data_plane).*")
public class RecordMetricActivityImpl implements RecordMetricActivity {

  @Inject
  private MetricClient metricClient;

  /**
   * Records a workflow counter for the specified metric.
   *
   * @param metricInput The information about the metric to record.
   */
  @Override
  public void recordWorkflowCountMetric(final RecordMetricInput metricInput) {
    final List<MetricAttribute> baseMetricAttributes = generateMetricAttributes(metricInput.getConnectionUpdaterInput());
    if (metricInput.getMetricAttributes() != null) {
      baseMetricAttributes.addAll(Stream.of(metricInput.getMetricAttributes()).collect(Collectors.toList()));
    }
    metricInput.getFailureCause().ifPresent(fc -> baseMetricAttributes.add(new MetricAttribute(MetricTags.RESET_WORKFLOW_FAILURE_CAUSE, fc.name())));
    metricClient.count(metricInput.getMetricName(), 1L, baseMetricAttributes.toArray(new MetricAttribute[] {}));
  }

  /**
   * Generates the list of {@link MetricAttribute}s to be included when recording a metric.
   *
   * @param connectionUpdaterInput The {@link ConnectionUpdaterInput} that represents the workflow to
   *        be executed.
   * @return The list of {@link MetricAttribute}s to be included when recording a metric.
   */
  private List<MetricAttribute> generateMetricAttributes(final ConnectionUpdaterInput connectionUpdaterInput) {
    final List<MetricAttribute> metricAttributes = new ArrayList<>();
    metricAttributes.add(new MetricAttribute(MetricTags.CONNECTION_ID, String.valueOf(connectionUpdaterInput.getConnectionId())));
    return metricAttributes;
  }

}
