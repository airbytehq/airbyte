/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.commons.json.Jsons;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.process.KubePodProcess;
import io.airbyte.workers.temporal.sync.OrchestratorConstants;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
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

  // reads the job run config from a file that was copied to the container launcher
  default JobRunConfig readJobRunConfig() throws IOException {
    return readAndDeserializeFile(Path.of(KubePodProcess.CONFIG_DIR, OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG), JobRunConfig.class);
  }

  /**
   * Contains the unique logic that belongs to each type of job.
   *
   * @return an optional output value to place within the output document store item.
   */
  Optional<String> runJob() throws Exception;

  static <T> T readAndDeserializeFile(String path, Class<T> type) throws IOException {
    return readAndDeserializeFile(Path.of(path), type);
  }

  static <T> T readAndDeserializeFile(Path path, Class<T> type) throws IOException {
    return Jsons.deserialize(Files.readString(path), type);
  }

}
