/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app.worker_run;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.JobOutput;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.WorkerUtils;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.Callable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/*
 * This class represents a single run of a worker. It handles making sure the correct inputs and
 * outputs are passed to the selected worker. It also makes sures that the outputs of the worker are
 * persisted to the db.
 */
public class WorkerRun implements Callable<OutputAndStatus<JobOutput>> {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerRun.class);

  private final Path jobRoot;
  private final CheckedSupplier<OutputAndStatus<JobOutput>, Exception> workerRun;

  public static WorkerRun create(Path workspaceRoot, long jobId, int attempt, CheckedSupplier<OutputAndStatus<JobOutput>, Exception> workerRun) {
    final Path jobRoot = WorkerUtils.getJobRoot(workspaceRoot, String.valueOf(jobId), attempt);
    return new WorkerRun(jobRoot, workerRun);
  }

  public WorkerRun(final Path jobRoot, final CheckedSupplier<OutputAndStatus<JobOutput>, Exception> workerRun) {
    this.jobRoot = jobRoot;
    this.workerRun = workerRun;
  }

  @Override
  public OutputAndStatus<JobOutput> call() throws Exception {
    LOGGER.info("Executing worker wrapper. Airbyte version: {}", new EnvConfigs().getAirbyteVersionOrWarning());
    Files.createDirectories(jobRoot);

    return workerRun.get();
  }

  public Path getJobRoot() {
    return jobRoot;
  }

}
