/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.tracker;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.config.JobOutput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.SyncStats;
import io.airbyte.persistence.job.models.Attempt;
import io.airbyte.persistence.job.models.AttemptStatus;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class TrackingMetadataTest {

  @Test
  void testNulls() {
    final UUID connectionId = UUID.randomUUID();
    final StandardSync standardSync = mock(StandardSync.class);

    // set all the required values for a valid connection
    when(standardSync.getConnectionId()).thenReturn(connectionId);
    when(standardSync.getName()).thenReturn("connection-name");
    when(standardSync.getManual()).thenReturn(true);
    when(standardSync.getSourceId()).thenReturn(UUID.randomUUID());
    when(standardSync.getDestinationId()).thenReturn(UUID.randomUUID());
    when(standardSync.getCatalog()).thenReturn(mock(ConfiguredAirbyteCatalog.class));
    when(standardSync.getResourceRequirements()).thenReturn(new ResourceRequirements());

    // make sure to use a null for resources
    when(standardSync.getCatalog()).thenReturn(mock(ConfiguredAirbyteCatalog.class));

    // try to generate metadata
    final Map<String, Object> expected = Map.of(
        "connection_id", connectionId,
        "frequency", "manual",
        "operation_count", 0,
        "table_prefix", false);
    final Map<String, Object> actual = TrackingMetadata.generateSyncMetadata(standardSync);
    assertEquals(expected, actual);
  }

  @Test
  void testgenerateJobAttemptMetadataWithNulls() {
    final SyncStats syncStats = new SyncStats().withRecordsCommitted(10L).withRecordsEmitted(10L).withBytesEmitted(100L)
        .withMeanSecondsBetweenStateMessageEmittedandCommitted(5L).withMaxSecondsBeforeSourceStateMessageEmitted(8L)
        .withMeanSecondsBeforeSourceStateMessageEmitted(2L).withMaxSecondsBetweenStateMessageEmittedandCommitted(null);
    final StandardSyncSummary standardSyncSummary = new StandardSyncSummary().withTotalStats(syncStats);
    final StandardSyncOutput standardSyncOutput = new StandardSyncOutput().withStandardSyncSummary(standardSyncSummary);
    final JobOutput jobOutput = new JobOutput().withSync(standardSyncOutput);
    final Attempt attempt = new Attempt(0, 10L, Path.of("test"), jobOutput, AttemptStatus.SUCCEEDED, null, null, 100L, 100L, 99L);
    final Job job = mock(Job.class);
    when(job.getAttempts()).thenReturn(List.of(attempt));

    final Map<String, Object> actual = TrackingMetadata.generateJobAttemptMetadata(job);
    final Map<String, Object> expected = Map.of(
        "mean_seconds_before_source_state_message_emitted", 2L,
        "mean_seconds_between_state_message_emit_and_commit", 5L,
        "max_seconds_before_source_state_message_emitted", 8L);
    assertEquals(expected, actual);
  }

}
