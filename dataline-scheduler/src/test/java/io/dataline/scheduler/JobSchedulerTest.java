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
import io.dataline.commons.functional.Factory;
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
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.integrations.Integrations;
import java.io.IOException;
import java.util.Collections;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JobSchedulerTest {

  private static final SourceConnectionImplementation sourceConnectionImplementation;
  private static final DestinationConnectionImplementation destinationConnectionImplementation;
  private static final StandardSync standardSync;
  private static final StandardSyncSchedule standardSyncSchedule;
  private static final long jobId = 12L;
  private static final Job previousJob;

  static {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceImplementationId = UUID.randomUUID();
    final UUID sourceSpecificationId = Integrations.POSTGRES_TAP.getSpecId();

    JsonNode implementationJson = Jsons.jsonNode(ImmutableMap.builder()
        .put("apiKey", "123-abc")
        .put("hostname", "dataline.io")
        .build());

    sourceConnectionImplementation = new SourceConnectionImplementation();
    sourceConnectionImplementation.setWorkspaceId(workspaceId);
    sourceConnectionImplementation.setSourceSpecificationId(sourceSpecificationId);
    sourceConnectionImplementation.setSourceImplementationId(sourceImplementationId);
    sourceConnectionImplementation.setConfiguration(implementationJson);
    sourceConnectionImplementation.setTombstone(false);

    final UUID destinationImplementationId = UUID.randomUUID();
    final UUID destinationSpecificationId = Integrations.POSTGRES_TARGET.getSpecId();

    destinationConnectionImplementation = new DestinationConnectionImplementation();
    destinationConnectionImplementation.setWorkspaceId(workspaceId);
    destinationConnectionImplementation.setDestinationSpecificationId(destinationSpecificationId);
    destinationConnectionImplementation.setDestinationImplementationId(destinationImplementationId);
    destinationConnectionImplementation.setConfiguration(implementationJson);

    final Column column = new Column();
    column.setDataType(DataType.STRING);
    column.setName("id");
    column.setSelected(true);

    final Table table = new Table();
    table.setName("users");
    table.setColumns(Lists.newArrayList(column));
    table.setSelected(true);

    final Schema schema = new Schema();
    schema.setTables(Lists.newArrayList(table));

    final UUID connectionId = UUID.randomUUID();

    standardSync = new StandardSync();
    standardSync.setConnectionId(connectionId);
    standardSync.setName("presto to hudi");
    standardSync.setStatus(StandardSync.Status.ACTIVE);
    standardSync.setSchema(schema);
    standardSync.setSourceImplementationId(sourceImplementationId);
    standardSync.setDestinationImplementationId(destinationImplementationId);
    standardSync.setSyncMode(StandardSync.SyncMode.APPEND);

    // empty. contents not needed for any of these unit tests.
    standardSyncSchedule = new StandardSyncSchedule();

    previousJob = new Job(
        jobId,
        "",
        null,
        null,
        null,
        null,
        null,
        1L,
        null,
        1L);
  }

  private ConfigPersistence configPersistence;
  private SchedulerPersistence schedulerPersistence;
  private ScheduleJobPredicate scheduleJobPredicate;
  private Factory<Long, UUID> jobFactory;
  private JobScheduler scheduler;

  @SuppressWarnings("unchecked")
  @BeforeEach
  public void setup() {
    configPersistence = mock(ConfigPersistence.class);
    schedulerPersistence = mock(SchedulerPersistence.class);

    scheduleJobPredicate = mock(ScheduleJobPredicate.class);
    jobFactory = (Factory<Long, UUID>) mock(Factory.class);
    scheduler = new JobScheduler(schedulerPersistence, configPersistence, scheduleJobPredicate, jobFactory);
  }

  @Test
  public void testScheduleJob() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(schedulerPersistence.getLastSyncJobForConnectionId(standardSync.getConnectionId()))
        .thenReturn(java.util.Optional.of(previousJob));
    when(scheduleJobPredicate.test(Optional.of(JobSchedulerTest.previousJob), standardSyncSchedule)).thenReturn(true);
    when(jobFactory.create(standardSync.getConnectionId())).thenReturn(jobId);
    setConfigMocks();

    scheduler.run();

    verifyConfigCalls();
    verify(scheduleJobPredicate).test(Optional.of(JobSchedulerTest.previousJob), standardSyncSchedule);
    verify(schedulerPersistence).getLastSyncJobForConnectionId(standardSync.getConnectionId());
    verify(jobFactory).create(standardSync.getConnectionId());
  }

  @Test
  public void testScheduleJobNoPreviousJob() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(schedulerPersistence.getLastSyncJobForConnectionId(standardSync.getConnectionId()))
        .thenReturn(java.util.Optional.empty());
    when(scheduleJobPredicate.test(Optional.empty(), standardSyncSchedule)).thenReturn(true);
    when(jobFactory.create(standardSync.getConnectionId())).thenReturn(jobId);
    setConfigMocks();

    scheduler.run();

    verifyConfigCalls();
    verify(scheduleJobPredicate).test(Optional.empty(), standardSyncSchedule);
    verify(schedulerPersistence).getLastSyncJobForConnectionId(standardSync.getConnectionId());
    verify(jobFactory).create(standardSync.getConnectionId());
  }

  @Test
  public void testDoNotScheduleJob() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(schedulerPersistence.getLastSyncJobForConnectionId(standardSync.getConnectionId()))
        .thenReturn(java.util.Optional.of(previousJob));
    when(scheduleJobPredicate.test(Optional.of(JobSchedulerTest.previousJob), standardSyncSchedule)).thenReturn(false);
    setConfigMocks();

    scheduler.run();

    verifyConfigCalls();
    verify(scheduleJobPredicate).test(Optional.of(JobSchedulerTest.previousJob), standardSyncSchedule);
    verify(schedulerPersistence).getLastSyncJobForConnectionId(standardSync.getConnectionId());
    verify(jobFactory, never()).create(standardSync.getConnectionId());
  }

  // sets all mocks that are related to fetching configs. these are the same for all tests in this
  // test suite.
  private void setConfigMocks() throws JsonValidationException, ConfigNotFoundException {
    when(configPersistence.getConfigs(PersistenceConfigType.STANDARD_SYNC, StandardSync.class))
        .thenReturn(Collections.singleton(standardSync));
    when(configPersistence.getConfig(
        PersistenceConfigType.STANDARD_SYNC_SCHEDULE,
        standardSync.getConnectionId().toString(),
        StandardSyncSchedule.class)).thenReturn(standardSyncSchedule);
  }

  // verify all mocks that are related to fetching configs are called. these are the same for all
  // tests in this test suite.
  private void verifyConfigCalls() throws JsonValidationException, ConfigNotFoundException {
    verify(configPersistence).getConfigs(PersistenceConfigType.STANDARD_SYNC, StandardSync.class);
    verify(configPersistence).getConfig(
        PersistenceConfigType.STANDARD_SYNC_SCHEDULE,
        standardSync.getConnectionId().toString(),
        StandardSyncSchedule.class);
  }

}
