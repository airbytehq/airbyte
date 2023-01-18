/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator.config;

import static org.junit.jupiter.api.Assertions.assertInstanceOf;

import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.micronaut.context.env.Environment;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import jakarta.inject.Inject;
import org.junit.jupiter.api.Test;

@MicronautTest(environments = Environment.KUBERNETES)
class ContainerOrchestratorFactoryK8sTest {

  @Inject
  ProcessFactory processFactory;

  @Test
  void processFactory() {
    assertInstanceOf(KubeProcessFactory.class, processFactory);
  }

}
