/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.config.Configs;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.db.Database;
import io.airbyte.scheduler.client.CachingSynchronousSchedulerClient;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.temporal.serviceclient.WorkflowServiceStubs;
import org.junit.jupiter.api.Test;

public class ConfigurationApiTest {

  @Test
  void testImportDefinitions() {
    final Configs configs = mock(Configs.class);
    when(configs.getWebappUrl()).thenReturn("http://localhost");

    final ConfigurationApi configurationApi = new ConfigurationApi(
        mock(ConfigRepository.class),
        mock(JobPersistence.class),
        mock(ConfigPersistence.class),
        mock(SchedulerJobClient.class),
        mock(CachingSynchronousSchedulerClient.class),
        configs,
        mock(FileTtlManager.class),
        mock(WorkflowServiceStubs.class),
        mock(Database.class),
        mock(Database.class),
        mock(TrackingClient.class));
    assertTrue(configurationApi.canImportDefinitons());
  }

}
