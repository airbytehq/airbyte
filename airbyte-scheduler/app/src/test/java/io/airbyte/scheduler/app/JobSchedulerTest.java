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

package io.airbyte.scheduler.app;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JobSchedulerTest {

  private static final StandardSync STANDARD_SYNC;
  private static final StandardSyncSchedule STANDARD_SYNC_SCHEDULE;
  private static final long JOB_ID = 12L;
  private Job previousJob;

  private static final String STREAM_NAME = "users";
  private static final String FIELD_NAME = "id";

  static {
    final UUID sourceId = UUID.randomUUID();

    final UUID destinationId = UUID.randomUUID();

    final ConfiguredAirbyteStream stream = new ConfiguredAirbyteStream()
        .withStream(CatalogHelpers.createAirbyteStream(STREAM_NAME, Field.of(FIELD_NAME, JsonSchemaPrimitive.STRING)));
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(stream));

    final UUID connectionId = UUID.randomUUID();

    STANDARD_SYNC = new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withPrefix("presto_to_hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withCatalog(catalog)
        .withSourceId(sourceId)
        .withDestinationId(destinationId);

    // empty. contents not needed for any of these unit tests.
    STANDARD_SYNC_SCHEDULE = new StandardSyncSchedule();
  }

  private ConfigRepository configRepository;
  private JobPersistence jobPersistence;
  private ScheduleJobPredicate scheduleJobPredicate;
  private SyncJobFactory jobFactory;
  private JobScheduler scheduler;

  @BeforeEach
  public void setup() {
    configRepository = mock(ConfigRepository.class);
    jobPersistence = mock(JobPersistence.class);

    scheduleJobPredicate = mock(ScheduleJobPredicate.class);
    jobFactory = mock(SyncJobFactory.class);
    scheduler = new JobScheduler(jobPersistence, configRepository, scheduleJobPredicate, jobFactory);

    previousJob = mock(Job.class);
  }

  @Test
  public void testScheduleJob() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(jobPersistence.getLastReplicationJob(STANDARD_SYNC.getConnectionId()))
        .thenReturn(java.util.Optional.of(previousJob));
    when(scheduleJobPredicate.test(Optional.of(previousJob), STANDARD_SYNC_SCHEDULE)).thenReturn(true);
    when(jobFactory.create(STANDARD_SYNC.getConnectionId())).thenReturn(JOB_ID);
    setConfigMocks();

    scheduler.run();

    verifyConfigCalls();
    verify(scheduleJobPredicate).test(Optional.of(previousJob), STANDARD_SYNC_SCHEDULE);
    verify(jobPersistence).getLastReplicationJob(STANDARD_SYNC.getConnectionId());
    verify(jobFactory).create(STANDARD_SYNC.getConnectionId());
  }

  @Test
  public void testScheduleJobNoPreviousJob() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(jobPersistence.getLastReplicationJob(STANDARD_SYNC.getConnectionId()))
        .thenReturn(java.util.Optional.empty());
    when(scheduleJobPredicate.test(Optional.empty(), STANDARD_SYNC_SCHEDULE)).thenReturn(true);
    when(jobFactory.create(STANDARD_SYNC.getConnectionId())).thenReturn(JOB_ID);
    setConfigMocks();

    scheduler.run();

    verifyConfigCalls();
    verify(scheduleJobPredicate).test(Optional.empty(), STANDARD_SYNC_SCHEDULE);
    verify(jobPersistence).getLastReplicationJob(STANDARD_SYNC.getConnectionId());
    verify(jobFactory).create(STANDARD_SYNC.getConnectionId());
  }

  @Test
  public void testDoNotScheduleJob() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(jobPersistence.getLastReplicationJob(STANDARD_SYNC.getConnectionId()))
        .thenReturn(java.util.Optional.of(previousJob));
    when(scheduleJobPredicate.test(Optional.of(previousJob), STANDARD_SYNC_SCHEDULE)).thenReturn(false);
    setConfigMocks();

    scheduler.run();

    verifyConfigCalls();
    verify(scheduleJobPredicate).test(Optional.of(previousJob), STANDARD_SYNC_SCHEDULE);
    verify(jobPersistence).getLastReplicationJob(STANDARD_SYNC.getConnectionId());
    verify(jobFactory, never()).create(STANDARD_SYNC.getConnectionId());
  }

  @Test
  public void testDoesNotScheduleNonActiveConnections() throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSync standardSync = Jsons.clone(STANDARD_SYNC);
    standardSync.setStatus(Status.INACTIVE);
    when(configRepository.listStandardSyncs()).thenReturn(Collections.singletonList(standardSync));

    scheduler.run();

    verify(configRepository).listStandardSyncs();
    verify(configRepository, never()).getStandardSyncSchedule(STANDARD_SYNC.getConnectionId());
    verify(scheduleJobPredicate, never()).test(Optional.of(previousJob), STANDARD_SYNC_SCHEDULE);
    verify(jobPersistence, never()).getLastReplicationJob(standardSync.getConnectionId());
    verify(jobFactory, never()).create(standardSync.getConnectionId());
  }

  // sets all mocks that are related to fetching configs. these are the same for all tests in this
  // test suite.
  private void setConfigMocks() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.listStandardSyncs()).thenReturn(Collections.singletonList(STANDARD_SYNC));
    when(configRepository.getStandardSyncSchedule(STANDARD_SYNC.getConnectionId())).thenReturn(STANDARD_SYNC_SCHEDULE);
  }

  // verify all mocks that are related to fetching configs are called. these are the same for all
  // tests in this test suite.
  private void verifyConfigCalls() throws ConfigNotFoundException, IOException, JsonValidationException {
    verify(configRepository).listStandardSyncs();
    verify(configRepository).getStandardSyncSchedule(STANDARD_SYNC.getConnectionId());
  }

}
