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

@SuppressWarnings("PMD.AvoidDuplicateLiterals")
@Factory
public class ConfigFactory {

  /**
   * Returns the config directory which contains all the configuration files.
   *
   * @param configDir optional directory, defaults to KubePodProcess.CONFIG_DIR if not defined.
   * @return Configuration directory.
   */
  @Singleton
  @Named("configDir")
  String configDir(@Value("${airbyte.config-dir}") @Nullable final String configDir) {
    if (configDir == null) {
      return KubePodProcess.CONFIG_DIR;
    }
    return configDir;
  }

  /**
   * Returns the contents of the OrchestratorConstants.INIT_FILE_APPLICATION file.
   *
   * @param configDir Which directory contains the OrchestratorConstants.INIT_FILE_APPLICATION file.
   * @return Contents of OrchestratorConstants.INIT_FILE_APPLICATION
   * @throws IOException
   */
  @Singleton
  @Named("application")
  String application(@Named("configDir") final String configDir) throws IOException {
    return Files.readString(Path.of(configDir, OrchestratorConstants.INIT_FILE_APPLICATION));
  }

  /**
   * Returns the contents of the OrchestratorConstants.INIT_FILE_ENV_MAP file.
   *
   * @param configDir Which directory contains the OrchestratorConstants.INIT_FILE_ENV_MAP file.
   * @return Contents of OrchestratorConstants.INIT_FILE_ENV_MAP
   */
  @Singleton
  @Named("envVars")
  Map<String, String> envVars(@Named("configDir") final String configDir) {
    return Jsons.deserialize(
        Path.of(configDir, OrchestratorConstants.INIT_FILE_ENV_MAP).toFile(), new TypeReference<>() {});
  }

  /**
   * Returns the contents of the OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG file.
   *
   * @param configDir Which directory contains the OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG
   *        file.
   * @return Contents of OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG
   */
  @Singleton
  JobRunConfig jobRunConfig(@Named("configDir") final String configDir) {
    return Jsons.deserialize(Path.of(configDir, OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG).toFile(), JobRunConfig.class);
  }

  /**
   * Returns the contents of the OrchestratorConstants.KUBE_POD_INFO file.
   *
   * @param configDir Which directory contains the OrchestratorConstants.KUBE_POD_INFO file.
   * @return Contents of OrchestratorConstants.KUBE_POD_INFO
   */
  @Singleton
  KubePodInfo kubePodInfo(@Named("configDir") final String configDir) {
    return Jsons.deserialize(Path.of(configDir, AsyncOrchestratorPodProcess.KUBE_POD_INFO).toFile(), KubePodInfo.class);
  }

}
