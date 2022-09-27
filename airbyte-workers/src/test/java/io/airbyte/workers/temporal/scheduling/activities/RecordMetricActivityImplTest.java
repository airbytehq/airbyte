/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.mockito.Mockito.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.temporal.scheduling.ConnectionUpdaterInput;
import io.airbyte.metrics.lib.MetricAttribute;
import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import io.airbyte.workers.temporal.scheduling.activities.RecordMetricActivity.FailureCause;
import io.airbyte.workers.temporal.scheduling.activities.RecordMetricActivity.RecordMetricInput;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link RecordMetricActivityImpl} class.
 */
class RecordMetricActivityImplTest {

  private MetricClient metricClient;

  private RecordMetricActivityImpl activity;

  @BeforeEach
  void setup() {
    metricClient = mock(MetricClient.class);
    activity = new RecordMetricActivityImpl(metricClient);
  }

  @Test
  void testRecordingMetricCounter() {
    final UUID connectionId = UUID.randomUUID();
    final OssMetricsRegistry metricName = OssMetricsRegistry.TEMPORAL_WORKFLOW_ATTEMPT;
    final ConnectionUpdaterInput connectionUpdaterInput = mock(ConnectionUpdaterInput.class);
    final RecordMetricInput metricInput = new RecordMetricInput(connectionUpdaterInput, Optional.empty(), metricName, null);

    when(connectionUpdaterInput.getConnectionId()).thenReturn(connectionId);

    activity.recordWorkflowCountMetric(metricInput);

    verify(metricClient).count(eq(metricName), eq(1L), eq(new MetricAttribute(MetricTags.CONNECTION_ID, String.valueOf(connectionId))));
  }

  @Test
  void testRecordingMetricCounterWithAdditionalAttributes() {
    final UUID connectionId = UUID.randomUUID();
    final OssMetricsRegistry metricName = OssMetricsRegistry.TEMPORAL_WORKFLOW_ATTEMPT;
    final ConnectionUpdaterInput connectionUpdaterInput = mock(ConnectionUpdaterInput.class);
    final MetricAttribute additionalAttribute = new MetricAttribute(MetricTags.JOB_STATUS, "test");
    final RecordMetricInput metricInput =
        new RecordMetricInput(connectionUpdaterInput, Optional.empty(), metricName, new MetricAttribute[] {additionalAttribute});

    when(connectionUpdaterInput.getConnectionId()).thenReturn(connectionId);

    activity.recordWorkflowCountMetric(metricInput);

    verify(metricClient).count(eq(metricName), eq(1L), eq(new MetricAttribute(MetricTags.CONNECTION_ID, String.valueOf(connectionId))),
        eq(additionalAttribute));
  }

  @Test
  void testRecordingMetricCounterWithFailureCause() {
    final UUID connectionId = UUID.randomUUID();
    final OssMetricsRegistry metricName = OssMetricsRegistry.TEMPORAL_WORKFLOW_ATTEMPT;
    final ConnectionUpdaterInput connectionUpdaterInput = mock(ConnectionUpdaterInput.class);
    final FailureCause failureCause = FailureCause.CANCELED;
    final RecordMetricInput metricInput = new RecordMetricInput(connectionUpdaterInput, Optional.of(failureCause), metricName, null);

    when(connectionUpdaterInput.getConnectionId()).thenReturn(connectionId);

    activity.recordWorkflowCountMetric(metricInput);

    verify(metricClient).count(eq(metricName), eq(1L), eq(new MetricAttribute(MetricTags.CONNECTION_ID, String.valueOf(connectionId))),
        eq(new MetricAttribute(MetricTags.RESET_WORKFLOW_FAILURE_CAUSE, failureCause.name())));
  }

}
