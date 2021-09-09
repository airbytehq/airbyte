/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.workers.temporal;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.db.Database;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerUtils;
import io.temporal.activity.Activity;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Duration;
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

/*
 * This class represents a single run of a worker. It handles making sure the correct inputs and
 * outputs are passed to the selected worker. It also makes sures that the outputs of the worker are
 * persisted to the db.
 */
public class TemporalAttemptExecution<INPUT, OUTPUT> implements Supplier<OUTPUT> {

  private static final Logger LOGGER = LoggerFactory.getLogger(TemporalAttemptExecution.class);

  private static final Duration HEARTBEAT_INTERVAL = Duration.ofSeconds(10);

  private final JobRunConfig jobRunConfig;
  private final Path jobRoot;
  private final CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier;
  private final Supplier<INPUT> inputSupplier;
  private final Consumer<Path> mdcSetter;
  private final CancellationHandler cancellationHandler;
  private final Supplier<String> workflowIdProvider;
  private final Configs configs;

  public TemporalAttemptExecution(Path workspaceRoot,
                                  JobRunConfig jobRunConfig,
                                  CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier,
                                  Supplier<INPUT> inputSupplier,
                                  CancellationHandler cancellationHandler) {
    this(
        workspaceRoot,
        jobRunConfig,
        workerSupplier,
        inputSupplier,
        LogClientSingleton::setJobMdc,
        cancellationHandler,
        () -> Activity.getExecutionContext().getInfo().getWorkflowId(),
        new EnvConfigs());
  }

  @VisibleForTesting
  TemporalAttemptExecution(Path workspaceRoot,
                           JobRunConfig jobRunConfig,
                           CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier,
                           Supplier<INPUT> inputSupplier,
                           Consumer<Path> mdcSetter,
                           CancellationHandler cancellationHandler,
                           Supplier<String> workflowIdProvider,
                           Configs configs) {
    this.jobRunConfig = jobRunConfig;
    this.jobRoot = WorkerUtils.getJobRoot(workspaceRoot, jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
    this.workerSupplier = workerSupplier;
    this.inputSupplier = inputSupplier;
    this.mdcSetter = mdcSetter;
    this.cancellationHandler = cancellationHandler;
    this.workflowIdProvider = workflowIdProvider;
    this.configs = configs;
  }

  @Override
  public OUTPUT get() {
    try {
      mdcSetter.accept(jobRoot);

      LOGGER.info("Executing worker wrapper. Airbyte version: {}", new EnvConfigs().getAirbyteVersionOrWarning());
      // TODO(Davin): This will eventually run into scaling problems, since it opens a DB connection per
      // workflow. See https://github.com/airbytehq/airbyte/issues/5936.
      saveWorkflowIdForCancellation();

      final Worker<INPUT, OUTPUT> worker = workerSupplier.get();
      final CompletableFuture<OUTPUT> outputFuture = new CompletableFuture<>();
      final Thread workerThread = getWorkerThread(worker, outputFuture);
      final ScheduledExecutorService scheduledExecutor = Executors.newSingleThreadScheduledExecutor();
      final Runnable cancellationChecker = getCancellationChecker(worker, workerThread, outputFuture);

      // check once first that we are not already cancelled. if we are, don't start!
      cancellationChecker.run();

      workerThread.start();
      scheduledExecutor.scheduleAtFixedRate(cancellationChecker, 0, HEARTBEAT_INTERVAL.toSeconds(), TimeUnit.SECONDS);

      try {
        // block and wait for the output
        return outputFuture.get();
      } finally {
        LOGGER.info("Stopping cancellation check scheduling...");
        scheduledExecutor.shutdown();
      }
    } catch (Exception e) {
      throw Activity.wrap(e);
    }
  }

  private void saveWorkflowIdForCancellation() throws IOException {
    // If the jobId is not a number, it means the job is a synchronous job. No attempt is created for
    // it, and it cannot be cancelled, so do not save the workflowId. See
    // SynchronousSchedulerClient.java
    // for info.
    if (NumberUtils.isCreatable(jobRunConfig.getJobId())) {
      final Database jobDatabase = new JobsDatabaseInstance(
          configs.getDatabaseUser(),
          configs.getDatabasePassword(),
          configs.getDatabaseUrl())
              .getInitialized();
      final JobPersistence jobPersistence = new DefaultJobPersistence(jobDatabase);
      final String workflowId = workflowIdProvider.get();
      jobPersistence.setAttemptTemporalWorkflowId(Long.parseLong(jobRunConfig.getJobId()), jobRunConfig.getAttemptId().intValue(), workflowId);
    }
  }

  private Thread getWorkerThread(Worker<INPUT, OUTPUT> worker, CompletableFuture<OUTPUT> outputFuture) {
    return new Thread(() -> {
      mdcSetter.accept(jobRoot);

      try {
        final OUTPUT output = worker.run(inputSupplier.get(), jobRoot);
        outputFuture.complete(output);
      } catch (Throwable e) {
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
   *
   * The callback defined in this function is executed after the above exception is caught, and
   * defines the clean up operations executed as part of cancel.
   *
   * See {@link CancellationHandler} for more info.
   */
  private Runnable getCancellationChecker(Worker<INPUT, OUTPUT> worker, Thread workerThread, CompletableFuture<OUTPUT> outputFuture) {
    var cancelled = new AtomicBoolean(false);
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
      } catch (Exception e) {
        LOGGER.error("Cancellation checker exception", e);
      }
    };
  }

}
