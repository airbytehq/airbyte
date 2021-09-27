/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JobSchedulerTest {

  private static final StandardSync STANDARD_SYNC;
  private static final List<StandardSyncOperation> STANDARD_SYNC_OPERATIONS;
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
    final UUID operationId = UUID.randomUUID();

    STANDARD_SYNC = new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withNamespaceDefinition(NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat(null)
        .withPrefix("presto_to_hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withCatalog(catalog)
        .withSourceId(sourceId)
        .withDestinationId(destinationId)
        .withOperationIds(List.of(operationId));

    // empty. contents not needed for any of these unit tests.
    STANDARD_SYNC_OPERATIONS = List.of(new StandardSyncOperation().withOperationId(operationId));
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
    when(scheduleJobPredicate.test(Optional.of(previousJob), STANDARD_SYNC)).thenReturn(true);
    when(jobFactory.create(STANDARD_SYNC.getConnectionId())).thenReturn(JOB_ID);
    setConfigMocks();

    scheduler.run();

    verifyConfigCalls();
    verify(scheduleJobPredicate).test(Optional.of(previousJob), STANDARD_SYNC);
    verify(jobPersistence).getLastReplicationJob(STANDARD_SYNC.getConnectionId());
    verify(jobFactory).create(STANDARD_SYNC.getConnectionId());
  }

  @Test
  public void testScheduleJobNoPreviousJob() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(jobPersistence.getLastReplicationJob(STANDARD_SYNC.getConnectionId()))
        .thenReturn(java.util.Optional.empty());
    when(scheduleJobPredicate.test(Optional.empty(), STANDARD_SYNC)).thenReturn(true);
    when(jobFactory.create(STANDARD_SYNC.getConnectionId())).thenReturn(JOB_ID);
    setConfigMocks();

    scheduler.run();

    verifyConfigCalls();
    verify(scheduleJobPredicate).test(Optional.empty(), STANDARD_SYNC);
    verify(jobPersistence).getLastReplicationJob(STANDARD_SYNC.getConnectionId());
    verify(jobFactory).create(STANDARD_SYNC.getConnectionId());
  }

  @Test
  public void testDoNotScheduleJob() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(jobPersistence.getLastReplicationJob(STANDARD_SYNC.getConnectionId()))
        .thenReturn(java.util.Optional.of(previousJob));
    when(scheduleJobPredicate.test(Optional.of(previousJob), STANDARD_SYNC)).thenReturn(false);
    setConfigMocks();

    scheduler.run();

    verifyConfigCalls();
    verify(scheduleJobPredicate).test(Optional.of(previousJob), STANDARD_SYNC);
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
    verify(scheduleJobPredicate, never()).test(Optional.of(previousJob), STANDARD_SYNC);
    verify(jobPersistence, never()).getLastReplicationJob(standardSync.getConnectionId());
    verify(jobFactory, never()).create(standardSync.getConnectionId());
  }

  // sets all mocks that are related to fetching configs. these are the same for all tests in this
  // test suite.
  private void setConfigMocks() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.listStandardSyncs()).thenReturn(Collections.singletonList(STANDARD_SYNC));
  }

  // verify all mocks that are related to fetching configs are called. these are the same for all
  // tests in this test suite.
  private void verifyConfigCalls() throws ConfigNotFoundException, IOException, JsonValidationException {
    verify(configRepository).listStandardSyncs();
  }

}
