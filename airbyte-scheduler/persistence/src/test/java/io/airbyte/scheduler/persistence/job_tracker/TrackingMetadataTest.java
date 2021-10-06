/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
