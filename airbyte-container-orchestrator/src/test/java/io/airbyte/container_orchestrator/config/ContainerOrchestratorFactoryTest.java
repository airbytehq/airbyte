/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.protocol.AirbyteMessageSerDeProvider;
import io.airbyte.commons.protocol.AirbyteMessageVersionedMigratorFactory;
import io.airbyte.config.EnvConfigs;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.process.AsyncOrchestratorPodProcess;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.sync.DbtLauncherWorker;
import io.airbyte.workers.sync.NormalizationLauncherWorker;
import io.airbyte.workers.sync.ReplicationLauncherWorker;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import jakarta.inject.Inject;
import org.junit.jupiter.api.Test;

@MicronautTest
class ContainerOrchestratorFactoryTest {

  @Inject
  FeatureFlags featureFlags;

  @Inject
  EnvConfigs envConfigs;

  @Inject
  WorkerConfigs workerConfigs;

  @Inject
  ProcessFactory processFactory;

  @Inject
  AirbyteMessageSerDeProvider airbyteMessageSerDeProvider;

  @Inject
  AirbyteMessageVersionedMigratorFactory airbyteMessageVersionedMigratorFactory;

  @Inject
  JobRunConfig jobRunConfig;

  // Tests will fail if this is uncommented, due to how the implementation of the DocumentStoreClient
  // is being created
  // @Inject
  // DocumentStoreClient documentStoreClient;

  @Test
  void featureFlags() {
    assertNotNull(featureFlags);
  }

  @Test
  void envConfigs() {
    // check one random environment variable to ensure the EnvConfigs was created correctly
    assertEquals("/tmp/airbyte_local", envConfigs.getEnv(EnvConfigs.LOCAL_DOCKER_MOUNT));
  }

  @Test
  void workerConfigs() {
    // check two variables to ensure the WorkerConfig was created correctly
    assertEquals("1", workerConfigs.getResourceRequirements().getCpuLimit());
    assertEquals("1Gi", workerConfigs.getResourceRequirements().getMemoryLimit());
  }

  @Test
  void processFactory() {
    assertInstanceOf(DockerProcessFactory.class, processFactory);
  }

  /**
   * There isn't an easy way to test the correct JobOrchestrator is injected using @MicronautTest
   * with @Nested classes, so opting for the more manual approach.
   */
  @Test
  void jobOrchestrator() {
    final var factory = new ContainerOrchestratorFactory();

    final var repl = factory.jobOrchestrator(
        ReplicationLauncherWorker.REPLICATION, envConfigs, processFactory, featureFlags, workerConfigs,
        airbyteMessageSerDeProvider, airbyteMessageVersionedMigratorFactory, jobRunConfig);
    assertEquals("Replication", repl.getOrchestratorName());

    final var norm = factory.jobOrchestrator(
        NormalizationLauncherWorker.NORMALIZATION, envConfigs, processFactory, featureFlags, workerConfigs,
        airbyteMessageSerDeProvider, airbyteMessageVersionedMigratorFactory, jobRunConfig);
    assertEquals("Normalization", norm.getOrchestratorName());

    final var dbt = factory.jobOrchestrator(
        DbtLauncherWorker.DBT, envConfigs, processFactory, featureFlags, workerConfigs,
        airbyteMessageSerDeProvider, airbyteMessageVersionedMigratorFactory, jobRunConfig);
    assertEquals("DBT Transformation", dbt.getOrchestratorName());

    final var noop = factory.jobOrchestrator(
        AsyncOrchestratorPodProcess.NO_OP, envConfigs, processFactory, featureFlags, workerConfigs,
        airbyteMessageSerDeProvider, airbyteMessageVersionedMigratorFactory, jobRunConfig);
    assertEquals("NO_OP", noop.getOrchestratorName());

    var caught = false;
    try {
      factory.jobOrchestrator(
          "does not exist", envConfigs, processFactory, featureFlags, workerConfigs,
          airbyteMessageSerDeProvider, airbyteMessageVersionedMigratorFactory, jobRunConfig);
    } catch (final Exception e) {
      caught = true;
    }
    assertTrue(caught, "invalid application name should have thrown an exception");
  }

}
