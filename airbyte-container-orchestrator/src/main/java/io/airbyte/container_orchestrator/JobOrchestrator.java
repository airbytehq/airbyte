/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.commons.json.Jsons;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.process.AsyncOrchestratorPodProcess;
import io.airbyte.workers.process.KubePodInfo;
import io.airbyte.workers.process.KubePodProcess;
import io.airbyte.workers.temporal.sync.OrchestratorConstants;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;

/**
 * The job orchestrator helps abstract over container launcher application differences across
 * replication, normalization, and custom dbt operators.
 *
 * @param <INPUT> job input type
 */
public interface JobOrchestrator<INPUT> {

  // used for logging
  String getOrchestratorName();

  // used to serialize the loaded input
  Class<INPUT> getInputClass();

  // reads input from a file that was copied to the container launcher
  default INPUT readInput() throws IOException {
    return readAndDeserializeFile(Path.of(KubePodProcess.CONFIG_DIR, OrchestratorConstants.INIT_FILE_INPUT), getInputClass());
  }

  /**
   * reads the application name from a file that was copied to the container launcher
   */
  static String readApplicationName() throws IOException {
    return Files.readString(Path.of(KubePodProcess.CONFIG_DIR, OrchestratorConstants.INIT_FILE_APPLICATION));
  }

  /**
   * reads the environment variable map from a file that was copied to the container launcher
   */
  static Map<String, String> readEnvMap() throws IOException {
    return (Map<String, String>) readAndDeserializeFile(Path.of(KubePodProcess.CONFIG_DIR, OrchestratorConstants.INIT_FILE_ENV_MAP), Map.class);
  }

  /**
   * reads the job run config from a file that was copied to the container launcher
   */
  static JobRunConfig readJobRunConfig() throws IOException {
    return readAndDeserializeFile(Path.of(KubePodProcess.CONFIG_DIR, OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG), JobRunConfig.class);
  }

  /**
   * reads the kube pod info from a file that was copied to the container launcher
   */
  static KubePodInfo readKubePodInfo() throws IOException {
    return readAndDeserializeFile(Path.of(KubePodProcess.CONFIG_DIR, AsyncOrchestratorPodProcess.KUBE_POD_INFO), KubePodInfo.class);
  }

  /**
   * Contains the unique logic that belongs to each type of job.
   *
   * @return an optional output value to place within the output document store item.
   */
  Optional<String> runJob() throws Exception;

  static <T> T readAndDeserializeFile(Path path, Class<T> type) throws IOException {
    return Jsons.deserialize(Files.readString(path), type);
  }

}
