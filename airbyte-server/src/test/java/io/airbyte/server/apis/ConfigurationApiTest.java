/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.db.Database;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.net.http.HttpClient;
import java.nio.file.Path;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.Test;

public class ConfigurationApiTest {

  @Test
  void testImportDefinitions() {
    final Configs configs = mock(Configs.class);
    when(configs.getAirbyteVersion()).thenReturn(new AirbyteVersion("0.1.0-alpha"));
    when(configs.getWebappUrl()).thenReturn("http://localhost");

    final ConfigurationApi configurationApi = new ConfigurationApi(
        mock(ConfigRepository.class),
        mock(JobPersistence.class),
        mock(ConfigPersistence.class),
        mock(SecretsRepositoryReader.class),
        mock(SecretsRepositoryWriter.class),
        mock(SynchronousSchedulerClient.class),
        mock(FileTtlManager.class),
        mock(Database.class),
        mock(Database.class),
        mock(StatePersistence.class),
        mock(TrackingClient.class),
        WorkerEnvironment.DOCKER,
        LogConfigs.EMPTY,
        new AirbyteVersion("0.1.0-alpha"),
        Path.of(""),
        mock(HttpClient.class),
        mock(EventRunner.class),
        mock(Flyway.class),
        mock(Flyway.class));
    assertTrue(configurationApi.canImportDefinitions());
  }

}
