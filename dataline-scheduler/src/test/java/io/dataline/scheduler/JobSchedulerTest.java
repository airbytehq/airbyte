/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.scheduler;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.dataline.commons.json.JsonValidationException;
import io.dataline.commons.json.Jsons;
import io.dataline.config.Column;
import io.dataline.config.DataType;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.Schema;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncSchedule;
import io.dataline.config.Table;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.integrations.Integrations;
import io.dataline.scheduler.job_factory.SyncJobFactory;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import java.io.IOException;
import java.util.Collections;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JobSchedulerTest {

  private static final SourceConnectionImplementation SOURCE_CONNECTION_IMPLEMENTATION;
  private static final DestinationConnectionImplementation DESTINATION_CONNECTION_IMPLEMENTATION;
  private static final StandardSync STANDARD_SYNC;
  private static final StandardSyncSchedule STANDARD_SYNC_SCHEDULE;
  private static final long JOB_ID = 12L;
  private Job previousJob;

  static {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceImplementationId = UUID.randomUUID();
    final UUID sourceSpecificationId = Integrations.POSTGRES_TAP.getSpecId();

    JsonNode implementationJson = Jsons.jsonNode(ImmutableMap.builder()
        .put("apiKey", "123-abc")
        .put("hostname", "dataline.io")
        .build());

    SOURCE_CONNECTION_IMPLEMENTATION = new SourceConnectionImplementation()
        .withWorkspaceId(workspaceId)
        .withSourceSpecificationId(sourceSpecificationId)
        .withSourceImplementationId(sourceImplementationId)
        .withConfiguration(implementationJson)
        .withTombstone(false);

    final UUID destinationImplementationId = UUID.randomUUID();
    final UUID destinationSpecificationId = Integrations.POSTGRES_TARGET.getSpecId();

    DESTINATION_CONNECTION_IMPLEMENTATION = new DestinationConnectionImplementation()
        .withWorkspaceId(workspaceId)
        .withDestinationSpecificationId(destinationSpecificationId)
        .withDestinationImplementationId(destinationImplementationId)
        .withConfiguration(implementationJson);

    final Column column = new Column()
        .withDataType(DataType.STRING)
        .withName("id")
        .withSelected(true);

    final Table table = new Table()
        .withName("users")
        .withColumns(Lists.newArrayList(column))
        .withSelected(true);

    final Schema schema = new Schema().withTables(Lists.newArrayList(table));

    final UUID connectionId = UUID.randomUUID();

    STANDARD_SYNC = new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withSchema(schema)
        .withSourceImplementationId(sourceImplementationId)
        .withDestinationImplementationId(destinationImplementationId)
        .withSyncMode(StandardSync.SyncMode.APPEND);

    // empty. contents not needed for any of these unit tests.
    STANDARD_SYNC_SCHEDULE = new StandardSyncSchedule();
  }

  private ConfigRepository configRepository;
  private SchedulerPersistence schedulerPersistence;
  private ScheduleJobPredicate scheduleJobPredicate;
  private SyncJobFactory jobFactory;
  private JobScheduler scheduler;

  @BeforeEach
  public void setup() {
    configRepository = mock(ConfigRepository.class);
    schedulerPersistence = mock(SchedulerPersistence.class);

    scheduleJobPredicate = mock(ScheduleJobPredicate.class);
    jobFactory = mock(SyncJobFactory.class);
    scheduler = new JobScheduler(schedulerPersistence, configRepository, scheduleJobPredicate, jobFactory);

    previousJob = mock(Job.class);
  }

  @Test
  public void testScheduleJob() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(schedulerPersistence.getLastSyncJob(STANDARD_SYNC.getConnectionId()))
        .thenReturn(java.util.Optional.of(previousJob));
    when(scheduleJobPredicate.test(Optional.of(previousJob), STANDARD_SYNC_SCHEDULE)).thenReturn(true);
    when(jobFactory.create(STANDARD_SYNC.getConnectionId())).thenReturn(JOB_ID);
    setConfigMocks();

    scheduler.run();

    verifyConfigCalls();
    verify(scheduleJobPredicate).test(Optional.of(previousJob), STANDARD_SYNC_SCHEDULE);
    verify(schedulerPersistence).getLastSyncJob(STANDARD_SYNC.getConnectionId());
    verify(jobFactory).create(STANDARD_SYNC.getConnectionId());
  }

  @Test
  public void testScheduleJobNoPreviousJob() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(schedulerPersistence.getLastSyncJob(STANDARD_SYNC.getConnectionId()))
        .thenReturn(java.util.Optional.empty());
    when(scheduleJobPredicate.test(Optional.empty(), STANDARD_SYNC_SCHEDULE)).thenReturn(true);
    when(jobFactory.create(STANDARD_SYNC.getConnectionId())).thenReturn(JOB_ID);
    setConfigMocks();

    scheduler.run();

    verifyConfigCalls();
    verify(scheduleJobPredicate).test(Optional.empty(), STANDARD_SYNC_SCHEDULE);
    verify(schedulerPersistence).getLastSyncJob(STANDARD_SYNC.getConnectionId());
    verify(jobFactory).create(STANDARD_SYNC.getConnectionId());
  }

  @Test
  public void testDoNotScheduleJob() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(schedulerPersistence.getLastSyncJob(STANDARD_SYNC.getConnectionId()))
        .thenReturn(java.util.Optional.of(previousJob));
    when(scheduleJobPredicate.test(Optional.of(previousJob), STANDARD_SYNC_SCHEDULE)).thenReturn(false);
    setConfigMocks();

    scheduler.run();

    verifyConfigCalls();
    verify(scheduleJobPredicate).test(Optional.of(previousJob), STANDARD_SYNC_SCHEDULE);
    verify(schedulerPersistence).getLastSyncJob(STANDARD_SYNC.getConnectionId());
    verify(jobFactory, never()).create(STANDARD_SYNC.getConnectionId());
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
