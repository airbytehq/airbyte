/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Sets;
import io.airbyte.commons.concurrency.LifecycledCallable;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.workers.worker_run.TemporalWorkerRunFactory;
import io.airbyte.workers.worker_run.WorkerRun;
import java.nio.file.Path;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class JobSubmitter implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobSubmitter.class);

  private final ExecutorService threadPool;
  private final JobPersistence persistence;
  private final TemporalWorkerRunFactory temporalWorkerRunFactory;
  private final JobTracker jobTracker;
  private final JobNotifier jobNotifier;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final ConfigRepository configRepository;

  // See attemptJobSubmit() to understand the need for this Concurrent Set.
  private final Set<Long> runningJobs = Sets.newConcurrentHashSet();

  public JobSubmitter(final ExecutorService threadPool,
                      final JobPersistence persistence,
                      final TemporalWorkerRunFactory temporalWorkerRunFactory,
                      final JobTracker jobTracker,
                      final JobNotifier jobNotifier,
                      final WorkerEnvironment workerEnvironment,
                      final LogConfigs logConfigs,
                      final ConfigRepository configRepository) {
    this.threadPool = threadPool;
    this.persistence = persistence;
    this.temporalWorkerRunFactory = temporalWorkerRunFactory;
    this.jobTracker = jobTracker;
    this.jobNotifier = jobNotifier;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.configRepository = configRepository;
  }

  @Override
  public void run() {
    try {
      LOGGER.debug("Running job-submitter...");
      final var start = System.currentTimeMillis();

      final Optional<Job> nextJob = persistence.getNextJob();

      nextJob.ifPresent(attemptJobSubmit());

      final var end = System.currentTimeMillis();
      LOGGER.debug("Completed Job-Submitter. Time taken: {} ms", end - start);
    } catch (final Throwable e) {
      LOGGER.error("Job Submitter Error", e);
    }
  }

  /**
   * Since job submission and job execution happen in two separate thread pools, and job execution is
   * what removes a job from the submission queue, it is possible for a job to be submitted multiple
   * times.
   * <p>
   * This synchronised block guarantees only a single thread can utilise the concurrent set to decide
   * whether a job should be submitted. This job id is added here, and removed in the finish block of
   * {@link #submitJob(Job)}.
   * <p>
   * Since {@link JobPersistence#getNextJob()} returns the next queued job, this solution cause
   * head-of-line blocking as the JobSubmitter tries to submit the same job. However, this suggests
   * the Worker Pool needs more workers and is inevitable when dealing with pending jobs.
   * <p>
   * See https://github.com/airbytehq/airbyte/issues/4378 for more info.
   */
  synchronized private Consumer<Job> attemptJobSubmit() {
    return job -> {
      if (!runningJobs.contains(job.getId())) {
        runningJobs.add(job.getId());
        trackSubmission(job);
        submitJob(job);
        final var pending = SchedulerApp.PENDING_JOBS.decrementAndGet();
        LOGGER.info("Job-Submitter Summary. Submitted job with scope {}", job.getScope());
        LOGGER.debug("Pending jobs: {}", pending);
      } else {
        LOGGER.info("Attempting to submit already running job {}. There are probably too many queued jobs.", job.getId());
        LOGGER.debug("Pending jobs: {}", SchedulerApp.PENDING_JOBS.get());
      }
    };
  }

  @VisibleForTesting
  void submitJob(final Job job) {

    final WorkerRun workerRun = temporalWorkerRunFactory.create(job);
    // we need to know the attempt number before we begin the job lifecycle. thus we state what the
    // attempt number should be. if it is not, that the lifecycle will fail. this should not happen as
    // long as job submission for a single job is single threaded. this is a compromise to allow the job
    // persistence to control what the attempt number should be while still allowing us to declare it
    // before the lifecycle begins.
    final int attemptNumber = job.getAttempts().size();
    threadPool.submit(new LifecycledCallable.Builder<>(workerRun)
        .setOnStart(() -> {
          // TODO(Issue-4204): This should save the fully qualified job path.
          final Path logFilePath = workerRun.getJobRoot().resolve(LogClientSingleton.LOG_FILENAME);
          final long persistedAttemptId = persistence.createAttempt(job.getId(), logFilePath);
          assertSameIds(attemptNumber, persistedAttemptId);
          LogClientSingleton.getInstance().setJobMdc(workerEnvironment, logConfigs, workerRun.getJobRoot());
        })
        .setOnSuccess(output -> {
          LOGGER.debug("Job id {} succeeded", job.getId());
          if (output.getOutput().isPresent()) {
            persistence.writeOutput(job.getId(), attemptNumber, output.getOutput().get());
          }

          if (output.getStatus() == io.airbyte.workers.JobStatus.SUCCEEDED) {
            persistence.succeedAttempt(job.getId(), attemptNumber);

            if (job.getConfigType() == ConfigType.SYNC) {
              final String connectionId = job.getScope();
              final StandardWorkspace workspace = configRepository.getStandardWorkspaceFromConnection(UUID.fromString(connectionId), false);

              if (workspace.getFirstCompletedSync() == null || !workspace.getFirstCompletedSync()) {
                workspace.setFirstCompletedSync(true);
                configRepository.writeStandardWorkspace(workspace);
              }

              jobNotifier.successJob(job);
            }
          } else {
            persistence.failAttempt(job.getId(), attemptNumber);
          }
          trackCompletion(job, output.getStatus());
        })
        .setOnException(e -> {
          LOGGER.error("Exception thrown in Job Submission: ", e);
          persistence.failAttempt(job.getId(), attemptNumber);
          trackCompletion(job, io.airbyte.workers.JobStatus.FAILED);
        })
        .setOnFinish(() -> {
          runningJobs.remove(job.getId());
          LOGGER.debug("Job id {} cleared", job.getId());
          MDC.clear();
        })
        .build());
  }

  private void assertSameIds(final long expectedAttemptId, final long actualAttemptId) {
    if (expectedAttemptId != actualAttemptId) {
      throw new IllegalStateException("Created attempt was not the expected attempt");
    }
  }

  private void trackSubmission(final Job job) {
    jobTracker.trackSync(job, JobState.STARTED);
  }

  private void trackCompletion(final Job job, final io.airbyte.workers.JobStatus status) {
    jobTracker.trackSync(job, Enums.convertTo(status, JobState.class));
  }

}
