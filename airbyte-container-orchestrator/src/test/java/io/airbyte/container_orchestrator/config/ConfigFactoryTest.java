/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator.config;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.process.KubePodInfo;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import java.util.Map;
import org.junit.jupiter.api.Test;

@MicronautTest
class ConfigFactoryTest {

  @Inject
  @Named("configDir")
  String configDir;

  @Inject
  @Named("application")
  String application;

  @Inject
  @Named("envVars")
  Map<String, String> envVars;

  @Inject
  JobRunConfig jobRunConfig;

  @Inject
  KubePodInfo kubePodInfo;

  @Test
  void configDir() {
    assertEquals("src/test/resources/files", configDir);
  }

  @Test
  void application() {
    assertEquals("normalization-orchestrator", application);
  }

  @Test
  void envVars() {
    assertEquals(29, envVars.size());
  }

  @Test
  void jobRunConfig() {
    assertEquals("824289", jobRunConfig.getJobId());
    assertEquals(10, jobRunConfig.getAttemptId());
  }

  @Test
  void kubePodInfo() {
    assertEquals("orchestrator-norm-job-824289-attempt-10", kubePodInfo.name());
    assertEquals("jobs", kubePodInfo.namespace());
    assertEquals("airbyte/container-orchestrator:dev-f0bb7a0ba3", kubePodInfo.mainContainerInfo().image());
    assertEquals("IfNotPresent", kubePodInfo.mainContainerInfo().pullPolicy());
  }

}
