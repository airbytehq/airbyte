/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.run;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.config.JobOutput;
import io.airbyte.workers.OutputAndStatus;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.Callable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/*
 * This class represents a single run of a worker. It handles making sure the correct inputs and
 * outputs are passed to the selected worker. It also makes sure that the outputs of the worker are
 * persisted to the db.
 */
@SuppressWarnings("PMD.AvoidFieldNameMatchingTypeName")
public class WorkerRun implements Callable<OutputAndStatus<JobOutput>> {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerRun.class);

  private final Path jobRoot;
  private final CheckedSupplier<OutputAndStatus<JobOutput>, Exception> workerRun;
  private final String airbyteVersionOrWarnings;

  public static WorkerRun create(final Path workspaceRoot,
                                 final long jobId,
                                 final int attempt,
                                 final CheckedSupplier<OutputAndStatus<JobOutput>, Exception> workerRun,
                                 final String airbyteVersionOrWarnings) {
    final Path jobRoot = TemporalUtils.getJobRoot(workspaceRoot, String.valueOf(jobId), attempt);
    return new WorkerRun(jobRoot, workerRun, airbyteVersionOrWarnings);
  }

  public WorkerRun(final Path jobRoot,
                   final CheckedSupplier<OutputAndStatus<JobOutput>, Exception> workerRun,
                   final String airbyteVersionOrWarnings) {
    this.jobRoot = jobRoot;
    this.workerRun = workerRun;
    this.airbyteVersionOrWarnings = airbyteVersionOrWarnings;
  }

  @Override
  public OutputAndStatus<JobOutput> call() throws Exception {
    LOGGER.info("Executing worker wrapper. Airbyte version: {}", airbyteVersionOrWarnings);
    Files.createDirectories(jobRoot);
    return workerRun.get();
  }

  public Path getJobRoot() {
    return jobRoot;
  }

}
