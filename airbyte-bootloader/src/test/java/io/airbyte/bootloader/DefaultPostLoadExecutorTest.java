/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.init.ApplyDefinitionsHelper;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

/**
 * Test suite for the {@link DefaultPostLoadExecutor} class.
 */
class DefaultPostLoadExecutorTest {

  @ParameterizedTest
  @CsvSource({"true,true,1", "true,false,1", "false,true,0", "false,false,1"})
  void testPostLoadExecution(final boolean forceSecretMigration, final boolean isSecretMigration, final int expectedTimes)
      throws Exception {
    final ApplyDefinitionsHelper applyDefinitionsHelper = mock(ApplyDefinitionsHelper.class);
    final FeatureFlags featureFlags = mock(FeatureFlags.class);
    final JobPersistence jobPersistence = mock(JobPersistence.class);
    final SecretMigrator secretMigrator = mock(SecretMigrator.class);

    when(featureFlags.forceSecretMigration()).thenReturn(forceSecretMigration);
    when(jobPersistence.isSecretMigrated()).thenReturn(isSecretMigration);

    final DefaultPostLoadExecutor postLoadExecution =
        new DefaultPostLoadExecutor(applyDefinitionsHelper, featureFlags, jobPersistence, secretMigrator);

    assertDoesNotThrow(() -> postLoadExecution.execute());
    verify(applyDefinitionsHelper, times(1)).apply();
    verify(secretMigrator, times(expectedTimes)).migrateSecrets();
  }

  @Test
  void testPostLoadExecutionNullSecretManager() throws JsonValidationException, IOException {
    final ApplyDefinitionsHelper applyDefinitionsHelper = mock(ApplyDefinitionsHelper.class);
    final FeatureFlags featureFlags = mock(FeatureFlags.class);
    final JobPersistence jobPersistence = mock(JobPersistence.class);

    when(featureFlags.forceSecretMigration()).thenReturn(true);

    final DefaultPostLoadExecutor postLoadExecution =
        new DefaultPostLoadExecutor(applyDefinitionsHelper, featureFlags, jobPersistence, null);

    assertDoesNotThrow(() -> postLoadExecution.execute());
    verify(applyDefinitionsHelper, times(1)).apply();
  }

  @Test
  void testPostLoadExecutionWithException() throws JsonValidationException, IOException {
    final ApplyDefinitionsHelper applyDefinitionsHelper = mock(ApplyDefinitionsHelper.class);
    final FeatureFlags featureFlags = mock(FeatureFlags.class);
    final JobPersistence jobPersistence = mock(JobPersistence.class);
    final SecretMigrator secretMigrator = mock(SecretMigrator.class);

    doThrow(new IOException("test")).when(applyDefinitionsHelper).apply();

    final DefaultPostLoadExecutor postLoadExecution =
        new DefaultPostLoadExecutor(applyDefinitionsHelper, featureFlags, jobPersistence, secretMigrator);

    assertThrows(IOException.class, () -> postLoadExecution.execute());
  }

}
