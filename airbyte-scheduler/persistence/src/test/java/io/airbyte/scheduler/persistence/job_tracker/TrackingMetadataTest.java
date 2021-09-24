/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_tracker;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSync;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class TrackingMetadataTest {

  @Test
  public void testNulls() {
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
    ImmutableMap<String, Object> expected = ImmutableMap.of(
        "connection_id", connectionId,
        "frequency", "manual",
        "operation_count", 0,
        "table_prefix", false);
    ImmutableMap<String, Object> actual = TrackingMetadata.generateSyncMetadata(standardSync);
    assertEquals(expected, actual);
  }

}
