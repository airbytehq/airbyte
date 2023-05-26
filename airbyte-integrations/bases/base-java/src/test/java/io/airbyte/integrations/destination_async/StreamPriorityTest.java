/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;

public class StreamPriorityTest {

  public static final Instant NOW = Instant.now();
  public static final Instant FIVE_MIN_AGO = NOW.minusSeconds(60 * 5);
  private static final StreamDescriptor DESC1 = new StreamDescriptor().withName("test1");
  private static final StreamDescriptor DESC2 = new StreamDescriptor().withName("test2");
  private static final Set<StreamDescriptor> DESCS = Set.of(DESC1, DESC2);

  @Test
  void testOrderByPrioritySize() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getQueueSizeBytes(DESC1)).thenReturn(Optional.of(1L)).thenReturn(Optional.of(0L));
    when(bufferDequeue.getQueueSizeBytes(DESC2)).thenReturn(Optional.of(0L)).thenReturn(Optional.of(1L));
    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, null, new AtomicBoolean(false), null);

    assertEquals(List.of(DESC1, DESC2), detect.orderStreamsByPriority(DESCS));
    assertEquals(List.of(DESC2, DESC1), detect.orderStreamsByPriority(DESCS));
  }

  @Test
  void testOrderByPrioritySecondarySortByTime() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getQueueSizeBytes(any())).thenReturn(Optional.of(0L));
    when(bufferDequeue.getTimeOfLastRecord(DESC1)).thenReturn(Optional.of(FIVE_MIN_AGO)).thenReturn(Optional.of(NOW));
    when(bufferDequeue.getTimeOfLastRecord(DESC2)).thenReturn(Optional.of(NOW)).thenReturn(Optional.of(FIVE_MIN_AGO));
    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, null, new AtomicBoolean(false), null);
    assertEquals(List.of(DESC1, DESC2), detect.orderStreamsByPriority(DESCS));
    assertEquals(List.of(DESC2, DESC1), detect.orderStreamsByPriority(DESCS));
  }

  @Test
  void testOrderByPriorityTertiarySortByName() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getQueueSizeBytes(any())).thenReturn(Optional.of(0L));
    when(bufferDequeue.getTimeOfLastRecord(any())).thenReturn(Optional.of(NOW));
    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, null, new AtomicBoolean(false), null);
    final List<StreamDescriptor> descs = List.of(Jsons.clone(DESC1), Jsons.clone(DESC2));
    assertEquals(List.of(descs.get(0), descs.get(1)), detect.orderStreamsByPriority(new HashSet<>(descs)));
    descs.get(0).setName("test3");
    assertEquals(List.of(descs.get(1), descs.get(0)), detect.orderStreamsByPriority(new HashSet<>(descs)));
  }

}
