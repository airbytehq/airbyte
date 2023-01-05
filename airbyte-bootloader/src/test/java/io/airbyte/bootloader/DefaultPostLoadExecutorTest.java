package io.airbyte.bootloader;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.init.DefinitionsProvider;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

/**
 * Test suite for the {@link DefaultPostLoadExecutor} class.
 */
class DefaultPostLoadExecutorTest {

  @ParameterizedTest
  @CsvSource({"true,true,1", "true,false,1", "false,true,0", "false,false,1"})
  void testPostLoadExecution(final boolean forceSecretMigration, final boolean isSecretMigration, final int expectedTimes) throws JsonValidationException, ConfigNotFoundException, IOException {
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final DefinitionsProvider definitionsProvider = mock(DefinitionsProvider.class);
    final FeatureFlags featureFlags = mock(FeatureFlags.class);
    final JobPersistence jobPersistence = mock(JobPersistence.class);
    final SecretMigrator secretMigrator = mock(SecretMigrator.class);

    when(featureFlags.forceSecretMigration()).thenReturn(forceSecretMigration);
    when(jobPersistence.isSecretMigrated()).thenReturn(isSecretMigration);

    final DefaultPostLoadExecutor postLoadExecution = new DefaultPostLoadExecutor(configRepository, Optional.of(definitionsProvider), featureFlags, jobPersistence, secretMigrator);

    assertDoesNotThrow(() -> postLoadExecution.execute());
    verify(secretMigrator, times(expectedTimes)).migrateSecrets();
  }

  @Test
  void testPostLoadExecutionNullSecretManager() {
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final DefinitionsProvider definitionsProvider = mock(DefinitionsProvider.class);
    final FeatureFlags featureFlags = mock(FeatureFlags.class);
    final JobPersistence jobPersistence = mock(JobPersistence.class);

    when(featureFlags.forceSecretMigration()).thenReturn(true);

    final DefaultPostLoadExecutor postLoadExecution = new DefaultPostLoadExecutor(configRepository, Optional.of(definitionsProvider), featureFlags, jobPersistence, null);

    assertDoesNotThrow(() -> postLoadExecution.execute());
  }

  @Test
  void testPostLoadExecutionWithException() throws JsonValidationException, IOException {
    final ConfigRepository configRepository = mock(ConfigRepository.class);
    final DefinitionsProvider definitionsProvider = mock(DefinitionsProvider.class);
    final FeatureFlags featureFlags = mock(FeatureFlags.class);
    final JobPersistence jobPersistence = mock(JobPersistence.class);
    final SecretMigrator secretMigrator = mock(SecretMigrator.class);

    doThrow(new IOException("test")).when(configRepository).seedActorDefinitions(any(), any());

    final DefaultPostLoadExecutor postLoadExecution = new DefaultPostLoadExecutor(configRepository, Optional.of(definitionsProvider), featureFlags, jobPersistence, secretMigrator);

    assertThrows(IOException.class, () -> postLoadExecution.execute());
  }
}
