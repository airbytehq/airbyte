/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator.config;

import com.fasterxml.jackson.core.type.TypeReference;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.temporal.sync.OrchestratorConstants;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.process.AsyncOrchestratorPodProcess;
import io.airbyte.workers.process.KubePodInfo;
import io.airbyte.workers.process.KubePodProcess;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Value;
import jakarta.annotation.Nullable;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;

@Factory
public class ConfigFactory {

  @Singleton
  @Named("configDir")
  String configDir(@Value("${airbyte.config-dir}") @Nullable final String configDir) {
    if (configDir == null) {
      return KubePodProcess.CONFIG_DIR;
    }
    return configDir;
  }

  @Singleton
  @Named("application")
  String application(@Named("configDir") final String configDir) throws IOException {
    // return "NO_OP";
    return Files.readString(Path.of(configDir, OrchestratorConstants.INIT_FILE_APPLICATION));
  }

  @Singleton
  @Named("envs")
  Map<String, String> envs(@Named("configDir") final String configDir) {
    // return Map.of();
    return Jsons.deserialize(
        Path.of(configDir, OrchestratorConstants.INIT_FILE_ENV_MAP).toFile(), new TypeReference<>() {});
  }

  @Singleton
  JobRunConfig jobRunConfig(@Named("configDir") final String configDir) {
    // return new JobRunConfig().withJobId("1").withAttemptId(2L);
    return Jsons.deserialize(Path.of(configDir, OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG).toFile(), JobRunConfig.class);
  }

  @Singleton
  KubePodInfo kubePodInfo(@Named("configDir") final String configDir) {
    // return new KubePodInfo("namespace", "name", null);
    return Jsons.deserialize(Path.of(configDir, AsyncOrchestratorPodProcess.KUBE_POD_INFO).toFile(), KubePodInfo.class);
  }

}
