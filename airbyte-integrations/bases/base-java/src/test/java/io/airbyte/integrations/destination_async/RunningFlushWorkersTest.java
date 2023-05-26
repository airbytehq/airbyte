/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import io.airbyte.protocol.models.v0.StreamDescriptor;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class RunningFlushWorkersTest {

  private static final StreamDescriptor STREAM1 = new StreamDescriptor().withNamespace("namespace1").withName("stream1");
  private static final StreamDescriptor STREAM2 = new StreamDescriptor().withNamespace("namespace2").withName("stream2");

  private RunningFlushWorkers runningFlushWorkers;

  @BeforeEach
  public void setup() {
    runningFlushWorkers = new RunningFlushWorkers();
  }

  @Test
  public void testTrackFlushWorker() {
    assertThat(runningFlushWorkers.getNumFlushWorkers(STREAM1)).isEqualTo(0);
    runningFlushWorkers.trackFlushWorker(STREAM1);
    assertThat(runningFlushWorkers.getNumFlushWorkers(STREAM1)).isEqualTo(1);
  }

  @Test
  public void testCompleteFlushWorker() {
    runningFlushWorkers.trackFlushWorker(STREAM1);
    runningFlushWorkers.completeFlushWorker(STREAM1);
    assertThat(runningFlushWorkers.getNumFlushWorkers(STREAM1)).isEqualTo(0);
  }

  @Test
  public void testCompleteFlushWorkerWithoutTrackThrowsException() {
    assertThatThrownBy(() -> runningFlushWorkers.completeFlushWorker(STREAM1))
        .isInstanceOf(IllegalStateException.class)
        .hasMessageContaining("Cannot complete flush worker for stream that has not started.");
  }

  @Test
  public void testMultipleStreams() {
    runningFlushWorkers.trackFlushWorker(STREAM1);
    runningFlushWorkers.trackFlushWorker(STREAM2);
    assertThat(runningFlushWorkers.getNumFlushWorkers(STREAM1)).isEqualTo(1);
    assertThat(runningFlushWorkers.getNumFlushWorkers(STREAM2)).isEqualTo(1);
  }

}
