package io.airbyte.server.handlers;

import static org.mockito.Mockito.mock;

import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.JobPersistence;
import org.junit.jupiter.api.BeforeEach;

public class MigrationHandlerTest {

  private ConfigRepository configRepository;
  private JobPersistence jobPersistence;
  private MigrationHandler migrationHandler;

  @BeforeEach
  void setUp() {
    configRepository = mock(ConfigRepository.class);
    jobPersistence = mock(JobPersistence.class);
    migrationHandler = new MigrationHandler(configRepository, jobPersistence);
  }

  void testMigration() {
    migrationHandler.importData(migrationHandler.exportData());
    // TODO check before/after
  }

}
