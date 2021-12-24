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
 * This class makes it easier to specify
 *
 * @param <T> input type
 */
public interface JobOrchestrator<T> {

  String getOrchestratorName();

  Class<T> getInputClass();

  default T readInput() throws IOException {
    return readAndDeserializeFile(OrchestratorConstants.INIT_FILE_INPUT, getInputClass());
  }

  default JobRunConfig readJobRunConfig() throws IOException {
    return readAndDeserializeFile(OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG, JobRunConfig.class);
  }

  void runJob() throws Exception;

  static <T> T readAndDeserializeFile(String path, Class<T> type) throws IOException {
    return Jsons.deserialize(Files.readString(Path.of(path)), type);
  }

}
