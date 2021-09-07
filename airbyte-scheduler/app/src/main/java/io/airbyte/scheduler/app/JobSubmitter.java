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

package io.airbyte.scheduler.app;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Sets;
import io.airbyte.commons.concurrency.LifecycledCallable;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.scheduler.app.worker_run.TemporalWorkerRunFactory;
import io.airbyte.scheduler.app.worker_run.WorkerRun;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import java.nio.file.Path;
import java.util.Optional;
import java.util.Set;
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

  // See attemptJobSubmit() to understand the need for this Concurrent Set.
  private final Set<Long> runningJobs = Sets.newConcurrentHashSet();

  public JobSubmitter(final ExecutorService threadPool,
                      final JobPersistence persistence,
                      final TemporalWorkerRunFactory temporalWorkerRunFactory,
                      final JobTracker jobTracker,
                      final JobNotifier jobNotifier) {
    this.threadPool = threadPool;
    this.persistence = persistence;
    this.temporalWorkerRunFactory = temporalWorkerRunFactory;
    this.jobTracker = jobTracker;
    this.jobNotifier = jobNotifier;
  }

  @Override
  public void run() {
    try {
      LOGGER.debug("Running job-submitter...");

      final Optional<Job> nextJob = persistence.getNextJob();

      nextJob.ifPresent(attemptJobSubmit());

      LOGGER.debug("Completed Job-Submitter...");
    } catch (Throwable e) {
      LOGGER.error("Job Submitter Error", e);
    }
  }

  /**
   * Since job submission and job execution happen in two separate thread pools, and job execution is
   * what removes a job from the submission queue, it is possible for a job to be submitted multiple
   * times.
   *
   * This synchronised block guarantees only a single thread can utilise the concurrent set to decide
   * whether a job should be submitted. This job id is added here, and removed in the finish block of
   * {@link #submitJob(Job)}.
   *
   * Since {@link JobPersistence#getNextJob()} returns the next queued job, this solution cause
   * head-of-line blocking as the JobSubmitter tries to submit the same job. However, this suggests
   * the Worker Pool needs more workers and is inevitable when dealing with pending jobs.
   *
   * See https://github.com/airbytehq/airbyte/issues/4378 for more info.
   */
  synchronized private Consumer<Job> attemptJobSubmit() {
    return job -> {
      if (!runningJobs.contains(job.getId())) {
        runningJobs.add(job.getId());
        trackSubmission(job);
        submitJob(job);
        LOGGER.info("Job-Submitter Summary. Submitted job with scope {}", job.getScope());
      } else {
        LOGGER.info("Attempting to submit already running job {}. There are probably too many queued jobs.", job.getId());
      }
    };
  }

  @VisibleForTesting
  void submitJob(Job job) {
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
          LogClientSingleton.setJobMdc(workerRun.getJobRoot());
        })
        .setOnSuccess(output -> {
          if (output.getOutput().isPresent()) {
            persistence.writeOutput(job.getId(), attemptNumber, output.getOutput().get());
          }

          if (output.getStatus() == io.airbyte.workers.JobStatus.SUCCEEDED) {
            persistence.succeedAttempt(job.getId(), attemptNumber);
            if (job.getConfigType() == ConfigType.SYNC) {
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
          MDC.clear();
        })
        .build());
  }

  private void assertSameIds(long expectedAttemptId, long actualAttemptId) {
    if (expectedAttemptId != actualAttemptId) {
      throw new IllegalStateException("Created attempt was not the expected attempt");
    }
  }

  private void trackSubmission(Job job) {
    jobTracker.trackSync(job, JobState.STARTED);
  }

  private void trackCompletion(Job job, io.airbyte.workers.JobStatus status) {
    jobTracker.trackSync(job, Enums.convertTo(status, JobState.class));
  }

}
