/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.db.Database;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerUtils;
import io.temporal.activity.Activity;
import io.temporal.workflow.Async;
import io.temporal.workflow.CancellationScope;
import io.temporal.workflow.CompletablePromise;
import io.temporal.workflow.Functions;
import io.temporal.workflow.Workflow;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Duration;
import java.util.concurrent.CancellationException;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.apache.commons.lang3.math.NumberUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

/*
 * This class represents a single run of a worker. It handles making sure the correct inputs and
 * outputs are passed to the selected worker. It also makes sures that the outputs of the worker are
 * persisted to the db.
 */
public class TemporalAttemptExecution<INPUT, OUTPUT> implements Supplier<OUTPUT> {

  private static final Logger LOGGER = LoggerFactory.getLogger(TemporalAttemptExecution.class);

  private static final Duration HEARTBEAT_INTERVAL = Duration.ofSeconds(10);

  private final JobRunConfig jobRunConfig;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final Path jobRoot;
  private final CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier;
  private final Supplier<INPUT> inputSupplier;
  private final Consumer<Path> mdcSetter;
  private final CancellationHandler cancellationHandler;
  private final Supplier<String> workflowIdProvider;
  private final String databaseUser;
  private final String databasePassword;
  private final String databaseUrl;
  private final String airbyteVersion;

  public TemporalAttemptExecution(final Path workspaceRoot,
                                  final WorkerEnvironment workerEnvironment,
                                  final LogConfigs logConfigs,
                                  final JobRunConfig jobRunConfig,
                                  final CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier,
                                  final Supplier<INPUT> inputSupplier,
                                  final CancellationHandler cancellationHandler,
                                  final String databaseUser,
                                  final String databasePassword,
                                  final String databaseUrl,
                                  final String airbyteVersion) {
    this(
        workspaceRoot, workerEnvironment, logConfigs,
        jobRunConfig,
        workerSupplier,
        inputSupplier,
        (path -> LogClientSingleton.getInstance().setJobMdc(workerEnvironment, logConfigs, path)),
        cancellationHandler, databaseUser, databasePassword, databaseUrl,
        () -> Activity.getExecutionContext().getInfo().getWorkflowId(), airbyteVersion);
  }

  @VisibleForTesting
  TemporalAttemptExecution(final Path workspaceRoot,
                           final WorkerEnvironment workerEnvironment,
                           final LogConfigs logConfigs,
                           final JobRunConfig jobRunConfig,
                           final CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier,
                           final Supplier<INPUT> inputSupplier,
                           final Consumer<Path> mdcSetter,
                           final CancellationHandler cancellationHandler,
                           final String databaseUser,
                           final String databasePassword,
                           final String databaseUrl,
                           final Supplier<String> workflowIdProvider,
                           final String airbyteVersion) {
    this.jobRunConfig = jobRunConfig;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;

    this.jobRoot = WorkerUtils.getJobRoot(workspaceRoot, jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
    this.workerSupplier = workerSupplier;
    this.inputSupplier = inputSupplier;
    this.mdcSetter = mdcSetter;
    this.cancellationHandler = cancellationHandler;
    this.workflowIdProvider = workflowIdProvider;

    this.databaseUser = databaseUser;
    this.databasePassword = databasePassword;
    this.databaseUrl = databaseUrl;
    this.airbyteVersion = airbyteVersion;
  }

  @Override
  public OUTPUT get() {
    try {
      mdcSetter.accept(jobRoot);

      if (MDC.get(LogClientSingleton.JOB_LOG_PATH_MDC_KEY) != null) {
        LOGGER.info("Docker volume job log path: " + MDC.get(LogClientSingleton.JOB_LOG_PATH_MDC_KEY));
      } else if (MDC.get(LogClientSingleton.CLOUD_JOB_LOG_PATH_MDC_KEY) != null) {
        LOGGER.info("Cloud storage job log path: " + MDC.get(LogClientSingleton.CLOUD_JOB_LOG_PATH_MDC_KEY));
      }

      LOGGER.info("Executing worker wrapper. Airbyte version: {}", airbyteVersion);
      // TODO(Davin): This will eventually run into scaling problems, since it opens a DB connection per
      // workflow. See https://github.com/airbytehq/airbyte/issues/5936.
      saveWorkflowIdForCancellation(databaseUser, databasePassword, databaseUrl);

      final Worker<INPUT, OUTPUT> worker = workerSupplier.get();
      final CompletablePromise<OUTPUT> outputPromise = Workflow.newPromise();

      final CancellationScope cancellableWorkerScope = Workflow.newCancellationScope(() -> Async.procedure(getWorkerThread(worker, outputPromise)));

      // run the worker asynchronously
      cancellableWorkerScope.run();

      // handle cancellation
      while (!outputPromise.isCompleted() && !cancellableWorkerScope.isCancelRequested()) {
        final Runnable onCancellationCallback = () -> {
          if (cancellableWorkerScope.isCancelRequested()) {
            // Since this is a separate thread, race condition between the executor service shutting down and
            // this thread's next invocation can happen. This
            // check guarantees cancel operations are only executed once.
            return;
          }

          LOGGER.info("Running worker cancellation...");
          worker.cancel();

          LOGGER.info("Cancelling worker cancellation scope...");
          cancellableWorkerScope.cancel();

          LOGGER.info("Completing output future exceptionally...");
          outputPromise.completeExceptionally(new CancellationException());
        };

        cancellationHandler.checkAndHandleCancellation(onCancellationCallback);

        Workflow.sleep(HEARTBEAT_INTERVAL);
      }

      // at this point the promise should be completed successfully or exceptionally
      return outputPromise.get();
    } catch (final Exception e) {
      throw Activity.wrap(e);
    }
  }

  private void saveWorkflowIdForCancellation(final String databaseUser, final String databasePassword, final String databaseUrl) throws IOException {
    // If the jobId is not a number, it means the job is a synchronous job. No attempt is created for
    // it, and it cannot be cancelled, so do not save the workflowId. See
    // SynchronousSchedulerClient.java
    // for info.
    if (NumberUtils.isCreatable(jobRunConfig.getJobId())) {
      final Database jobDatabase = new JobsDatabaseInstance(
          databaseUser,
          databasePassword,
          databaseUrl)
              .getInitialized();
      final JobPersistence jobPersistence = new DefaultJobPersistence(jobDatabase);
      final String workflowId = workflowIdProvider.get();
      jobPersistence.setAttemptTemporalWorkflowId(Long.parseLong(jobRunConfig.getJobId()), jobRunConfig.getAttemptId().intValue(), workflowId);
    }
  }

  private Functions.Proc getWorkerThread(final Worker<INPUT, OUTPUT> worker, final CompletablePromise<OUTPUT> outputPromise) {
    return () -> {
      mdcSetter.accept(jobRoot);

      try {
        final OUTPUT output = worker.run(inputSupplier.get(), jobRoot);
        outputPromise.complete(output);
      } catch (final Throwable e) {
        LOGGER.info("Completing future exceptionally...", e);
        outputPromise.completeExceptionally(new RuntimeException(e));
      }
    };
  }

}
