/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerUtils;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import java.io.IOException;
import java.nio.file.Path;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
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
@SuppressWarnings({"PMD.UnusedFormalParameter", "PMD.AvoidCatchingThrowable"})
public class TemporalAttemptExecution<INPUT, OUTPUT> implements Supplier<OUTPUT> {

  private static final Logger LOGGER = LoggerFactory.getLogger(TemporalAttemptExecution.class);

  private final JobRunConfig jobRunConfig;
  private final Path jobRoot;
  private final CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier;
  private final Supplier<INPUT> inputSupplier;
  private final Consumer<Path> mdcSetter;
  private final CancellationHandler cancellationHandler;
  private final Supplier<String> workflowIdProvider;
  private final JobPersistence jobPersistence;
  private final String airbyteVersion;

  public TemporalAttemptExecution(final Path workspaceRoot,
                                  final WorkerEnvironment workerEnvironment,
                                  final LogConfigs logConfigs,
                                  final JobRunConfig jobRunConfig,
                                  final CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier,
                                  final Supplier<INPUT> inputSupplier,
                                  final CancellationHandler cancellationHandler,
                                  final JobPersistence jobPersistence,
                                  final String airbyteVersion,
                                  final Supplier<ActivityExecutionContext> activityContext) {
    this(
        workspaceRoot, workerEnvironment, logConfigs,
        jobRunConfig,
        workerSupplier,
        inputSupplier,
        (path -> LogClientSingleton.getInstance().setJobMdc(workerEnvironment, logConfigs, path)),
        cancellationHandler,
        jobPersistence,
        () -> activityContext.get().getInfo().getWorkflowId(),
        airbyteVersion);
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
                           final JobPersistence jobPersistence,
                           final Supplier<String> workflowIdProvider,
                           final String airbyteVersion) {
    this.jobRunConfig = jobRunConfig;

    this.jobRoot = WorkerUtils.getJobRoot(workspaceRoot, jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
    this.workerSupplier = workerSupplier;
    this.inputSupplier = inputSupplier;
    this.mdcSetter = mdcSetter;
    this.cancellationHandler = cancellationHandler;
    this.workflowIdProvider = workflowIdProvider;

    this.jobPersistence = jobPersistence;
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
      saveWorkflowIdForCancellation(jobPersistence);

      final Worker<INPUT, OUTPUT> worker = workerSupplier.get();
      final CompletableFuture<OUTPUT> outputFuture = new CompletableFuture<>();
      final Thread workerThread = getWorkerThread(worker, outputFuture);
      final ScheduledExecutorService scheduledExecutor = Executors.newSingleThreadScheduledExecutor();
      final Runnable cancellationChecker = getCancellationChecker(worker, workerThread, outputFuture);

      // check once first that we are not already cancelled. if we are, don't start!
      cancellationChecker.run();

      workerThread.start();
      scheduledExecutor.scheduleAtFixedRate(cancellationChecker, 0, TemporalUtils.SEND_HEARTBEAT_INTERVAL.toSeconds(), TimeUnit.SECONDS);

      try {
        // block and wait for the output
        return outputFuture.get();
      } finally {
        LOGGER.info("Stopping cancellation check scheduling...");
        scheduledExecutor.shutdown();
      }
    } catch (final Exception e) {
      throw Activity.wrap(e);
    }
  }

  private void saveWorkflowIdForCancellation(final JobPersistence jobPersistence) throws IOException {
    // If the jobId is not a number, it means the job is a synchronous job. No attempt is created for
    // it, and it cannot be cancelled, so do not save the workflowId. See
    // SynchronousSchedulerClient.java
    // for info.
    if (NumberUtils.isCreatable(jobRunConfig.getJobId())) {
      final String workflowId = workflowIdProvider.get();
      jobPersistence.setAttemptTemporalWorkflowId(Long.parseLong(jobRunConfig.getJobId()), jobRunConfig.getAttemptId().intValue(), workflowId);
    }
  }

  private Thread getWorkerThread(final Worker<INPUT, OUTPUT> worker, final CompletableFuture<OUTPUT> outputFuture) {
    return new Thread(() -> {
      mdcSetter.accept(jobRoot);

      try {
        final OUTPUT output = worker.run(inputSupplier.get(), jobRoot);
        outputFuture.complete(output);
      } catch (final Throwable e) {
        LOGGER.info("Completing future exceptionally...", e);
        outputFuture.completeExceptionally(e);
      }
    });
  }

  /**
   * Cancel is implementation in a slightly convoluted manner due to Temporal's semantics. Cancel
   * requests are routed to the Temporal Scheduler via the cancelJob function in
   * SchedulerHandler.java. This manifests as a {@link io.temporal.client.ActivityCompletionException}
   * when the {@link CancellationHandler} heartbeats to the Temporal Scheduler.
   * <p>
   * The callback defined in this function is executed after the above exception is caught, and
   * defines the clean up operations executed as part of cancel.
   * <p>
   * See {@link CancellationHandler} for more info.
   */
  private Runnable getCancellationChecker(final Worker<INPUT, OUTPUT> worker,
                                          final Thread workerThread,
                                          final CompletableFuture<OUTPUT> outputFuture) {
    final var cancelled = new AtomicBoolean(false);
    return () -> {
      try {
        mdcSetter.accept(jobRoot);

        final Runnable onCancellationCallback = () -> {
          if (cancelled.get()) {
            // Since this is a separate thread, race condition between the executor service shutting down and
            // this thread's next invocation can happen. This
            // check guarantees cancel operations are only executed once.
            return;
          }

          LOGGER.info("Running sync worker cancellation...");
          cancelled.set(true);
          worker.cancel();

          LOGGER.info("Interrupting worker thread...");
          workerThread.interrupt();

          LOGGER.info("Cancelling completable future...");
          // This throws a CancellationException as part of the cancelling and is the exception seen in logs
          // when cancelling the job.
          outputFuture.cancel(false);
        };

        cancellationHandler.checkAndHandleCancellation(onCancellationCallback);
      } catch (final Exception e) {
        LOGGER.error("Cancellation checker exception", e);
      }
    };
  }

}
