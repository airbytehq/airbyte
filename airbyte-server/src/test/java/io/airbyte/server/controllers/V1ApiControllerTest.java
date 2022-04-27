/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.controllers;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.handlers.ArchiveHandler;
import io.airbyte.server.handlers.JobHistoryHandler;
import io.airbyte.workers.temporal.TemporalClient;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.env.Environment;
import io.micronaut.core.util.StringUtils;
import io.micronaut.test.annotation.MockBean;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import io.temporal.serviceclient.WorkflowServiceStubs;
import javax.inject.Inject;
import org.junit.jupiter.api.Test;

@MicronautTest
@Requires(env = {Environment.TEST})
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.FALSE,
          value = StringUtils.TRUE)
public class V1ApiControllerTest {

  @Inject
  private V1ApiController v1ApiController;

  @Inject
  private ArchiveHandler archiveHandler;

  @MockBean(ConfigRepository.class)
  ConfigRepository configRepository() {
    return mock(ConfigRepository.class);
  }

  @MockBean(JobPersistence.class)
  JobPersistence jobPersistence() {
    return mock(JobPersistence.class);
  }

  @MockBean(ConfigPersistence.class)
  ConfigPersistence configPersistence() {
    return mock(ConfigPersistence.class);
  }

  @MockBean(SecretsRepositoryReader.class)
  SecretsRepositoryReader secretsRepositoryReader() {
    return mock(SecretsRepositoryReader.class);
  }

  @MockBean(SecretsRepositoryWriter.class)
  SecretsRepositoryWriter secretsRepositoryWriter() {
    return mock(SecretsRepositoryWriter.class);
  }

  @MockBean(FileTtlManager.class)
  FileTtlManager fileTtlManager() {
    return mock(FileTtlManager.class);
  }

  @MockBean(LogConfigs.class)
  LogConfigs logConfigs() {
    return LogConfigs.EMPTY;
  }

  @MockBean(AirbyteVersion.class)
  AirbyteVersion airbyteVersion() {
    return new AirbyteVersion("0.1.0-alpha");
  }

  @MockBean(FeatureFlags.class)
  FeatureFlags featureFlags() {
    return mock(FeatureFlags.class);
  }

  @MockBean(EventRunner.class)
  EventRunner eventRunner() {
    return mock(EventRunner.class);
  }

  @MockBean(ArchiveHandler.class)
  ArchiveHandler archiveHandler() {
    return mock(ArchiveHandler.class);
  }

  @MockBean(JobHistoryHandler.class)
  JobHistoryHandler jobHistoryHandler() {
    return mock(JobHistoryHandler.class);
  }

  @MockBean(TrackingClient.class)
  TrackingClient trackingClient() {
    return mock(TrackingClient.class);
  }

  @MockBean(TemporalClient.class)
  TemporalClient temporalClient() {
    return mock(TemporalClient.class);
  }

  @MockBean(WorkflowServiceStubs.class)
  WorkflowServiceStubs temporalService() {
    return mock(WorkflowServiceStubs.class);
  }

  @Test
  void testImportDefinitions() {
    when(archiveHandler.canImportDefinitions()).thenReturn(true);
    assertTrue(v1ApiController.canImportDefinitions());
    verify(archiveHandler, times(1)).canImportDefinitions();
  }

}
