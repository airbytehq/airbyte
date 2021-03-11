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

package io.airbyte.scheduler.client;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.postgresql.hostchooser.HostRequirement.any;

import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.scheduler.JobTracker;
import io.airbyte.scheduler.JobTracker.JobState;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalJobException;
import java.nio.file.Path;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultSynchronousSchedulerClientTest {

  private TemporalClient temporalClient;
  private JobTracker jobTracker;
  private DefaultSynchronousSchedulerClient schedulerClient;

  @BeforeEach
  void setup() {
    temporalClient = mock(TemporalClient.class);
    jobTracker = mock(JobTracker.class);
    schedulerClient = new DefaultSynchronousSchedulerClient(temporalClient, jobTracker);
  }

  @SuppressWarnings("unchecked")
  @Test
  void testExecute() throws TemporalJobException {
    final UUID configId = UUID.randomUUID();
    final UUID jobTrackingId = UUID.randomUUID();
    final CheckedFunction<UUID, String, TemporalJobException> checkedFunction = mock(CheckedFunction.class);
    when(checkedFunction.apply(any(UUID.class))).thenReturn("hello");

    final SynchronousResponse<String> response = schedulerClient.execute(ConfigType.DISCOVER_SCHEMA, configId, checkedFunction, jobTrackingId);

    assertNotNull(response);
    assertEquals("hello", response.getOutput());
    assertEquals(ConfigType.DISCOVER_SCHEMA, response.getMetadata().getConfigType());
    assertTrue(response.getMetadata().getConfigId().isPresent());
    assertEquals(configId, response.getMetadata().getConfigId().get());
    assertTrue(response.getMetadata().isSucceeded());
    assertTrue(response.getMetadata().getLogPath().isEmpty());

    verify(jobTracker).trackDiscover(any(UUID.class), eq(jobTrackingId), eq(JobState.STARTED));
    verify(jobTracker).trackDiscover(any(UUID.class), eq(jobTrackingId), eq(JobState.SUCCEEDED));
  }

  @SuppressWarnings("unchecked")
  @Test
  void testExecuteTemporalJobException() throws TemporalJobException {
    final UUID configId = UUID.randomUUID();
    final UUID jobTrackingId = UUID.randomUUID();
    final CheckedFunction<UUID, String, TemporalJobException> checkedFunction = mock(CheckedFunction.class);
    when(checkedFunction.apply(any(UUID.class))).thenThrow(new TemporalJobException(Path.of("/tmp")));

    final SynchronousResponse<String> response = schedulerClient.execute(ConfigType.DISCOVER_SCHEMA, configId, checkedFunction, jobTrackingId);

    assertNotNull(response);
    assertNull(response.getOutput());
    assertEquals(ConfigType.DISCOVER_SCHEMA, response.getMetadata().getConfigType());
    assertTrue(response.getMetadata().getConfigId().isPresent());
    assertEquals(configId, response.getMetadata().getConfigId().get());
    assertFalse(response.getMetadata().isSucceeded());
    assertTrue(response.getMetadata().getLogPath().isPresent());

    verify(jobTracker).trackDiscover(any(UUID.class), eq(jobTrackingId), eq(JobState.STARTED));
    verify(jobTracker).trackDiscover(any(UUID.class), eq(jobTrackingId), eq(JobState.FAILED));
  }

  @SuppressWarnings("unchecked")
  @Test
  void testExecuteRuntimeException() throws TemporalJobException {
    final UUID configId = UUID.randomUUID();
    final UUID jobTrackingId = UUID.randomUUID();
    final CheckedFunction<UUID, String, TemporalJobException> checkedFunction = mock(CheckedFunction.class);
    when(checkedFunction.apply(any(UUID.class))).thenThrow(new RuntimeException());

    assertThrows(RuntimeException.class, () -> schedulerClient.execute(ConfigType.DISCOVER_SCHEMA, configId, checkedFunction, jobTrackingId));

    verify(jobTracker).trackDiscover(any(UUID.class), eq(jobTrackingId), eq(JobState.STARTED));
    verify(jobTracker).trackDiscover(any(UUID.class), eq(jobTrackingId), eq(JobState.FAILED));
  }

}
