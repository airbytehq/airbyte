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
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.io.IOs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.temporal.activity.Activity;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.function.BiConsumer;
import java.util.function.Supplier;
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

  public static String WORKFLOW_ID_FILENAME = "WORKFLOW_ID";

  private final Path jobRoot;
  private final CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier;
  private final Supplier<INPUT> inputSupplier;
  private final String jobId;
  private final BiConsumer<Path, String> mdcSetter;
  private final CheckedConsumer<Path, IOException> jobRootDirCreator;
  private final CancellationHandler cancellationHandler;
  private final Supplier<String> workflowIdProvider;

  public TemporalAttemptExecution(Path workspaceRoot,
                                  JobRunConfig jobRunConfig,
                                  CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier,
                                  Supplier<INPUT> inputSupplier,
                                  CancellationHandler cancellationHandler) {
    this(workspaceRoot, jobRunConfig, workerSupplier, inputSupplier, WorkerUtils::setJobMdc, Files::createDirectories, cancellationHandler,
        () -> Activity.getExecutionContext().getInfo().getWorkflowId());
  }

  @VisibleForTesting
  TemporalAttemptExecution(Path workspaceRoot,
                           JobRunConfig jobRunConfig,
                           CheckedSupplier<Worker<INPUT, OUTPUT>, Exception> workerSupplier,
                           Supplier<INPUT> inputSupplier,
                           BiConsumer<Path, String> mdcSetter,
                           CheckedConsumer<Path, IOException> jobRootDirCreator,
                           CancellationHandler cancellationHandler,
                           Supplier<String> workflowIdProvider) {
    this.jobRoot = WorkerUtils.getJobRoot(workspaceRoot, jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
    this.workerSupplier = workerSupplier;
    this.inputSupplier = inputSupplier;
    this.jobId = jobRunConfig.getJobId();
    this.mdcSetter = mdcSetter;
    this.jobRootDirCreator = jobRootDirCreator;
    this.cancellationHandler = cancellationHandler;
    this.workflowIdProvider = workflowIdProvider;
  }

  @Override
  public OUTPUT get() {
    try {
      mdcSetter.accept(jobRoot, jobId);

      LOGGER.info("Executing worker wrapper. Airbyte version: {}", new EnvConfigs().getAirbyteVersionOrWarning());
      jobRootDirCreator.accept(jobRoot);

      final String workflowId = workflowIdProvider.get();
      final Path workflowIdFile = jobRoot.getParent().resolve(WORKFLOW_ID_FILENAME);
      IOs.writeFile(workflowIdFile, workflowId);

      final Worker<INPUT, OUTPUT> worker = workerSupplier.get();
      final CompletableFuture<OUTPUT> outputFuture = new CompletableFuture<>();
      final Thread workerThread = getWorkerThread(worker, outputFuture);
      final ScheduledExecutorService scheduledExecutor = Executors.newSingleThreadScheduledExecutor();
      final Runnable cancellationChecker = getCancellationChecker(worker, workerThread, outputFuture);

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

  private Thread getWorkerThread(Worker<INPUT, OUTPUT> worker, CompletableFuture<OUTPUT> outputFuture) {
    return new Thread(() -> {
      mdcSetter.accept(jobRoot, jobId);

      try {
        final OUTPUT output = worker.run(inputSupplier.get(), jobRoot);
        outputFuture.complete(output);
      } catch (Throwable e) {
        LOGGER.info("Completing future exceptionally...", e);
        outputFuture.completeExceptionally(e);
      }
    });
  }

  private Runnable getCancellationChecker(Worker<INPUT, OUTPUT> worker, Thread workerThread, CompletableFuture<OUTPUT> outputFuture) {
    return () -> {
      try {
        mdcSetter.accept(jobRoot, jobId);

        final Runnable onCancellationCallback = () -> {
          LOGGER.info("Running sync worker cancellation...");
          worker.cancel();

          LOGGER.info("Interrupting worker thread...");
          workerThread.interrupt();

          LOGGER.info("Cancelling completable future...");
          outputFuture.cancel(false);
        };

        cancellationHandler.checkAndHandleCancellation(onCancellationCallback);
      } catch (WorkerException e) {
        LOGGER.error("Cancellation checker exception", e);
      }
    };
  }

}
