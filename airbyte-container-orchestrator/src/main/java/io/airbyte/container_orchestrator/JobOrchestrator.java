/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.commons.json.Jsons;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.sync.OrchestratorConstants;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

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
    return readAndDeserializeFile(OrchestratorConstants.INIT_FILE_INPUT, getInputClass());
  }

  // reads the job run config from a file that was copied to the container launcher
  default JobRunConfig readJobRunConfig() throws IOException {
    return readAndDeserializeFile(OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG, JobRunConfig.class);
  }

  // the unique logic that belongs to each type of job belongs here
  void runJob() throws Exception;

  static <T> T readAndDeserializeFile(String path, Class<T> type) throws IOException {
    return Jsons.deserialize(Files.readString(Path.of(path)), type);
  }

}
