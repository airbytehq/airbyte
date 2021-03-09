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

package io.airbyte.scheduler.temporal;

import com.google.common.base.Preconditions;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.workers.DefaultSyncWorker;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageTracker;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteDestination;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
import io.airbyte.workers.protocols.airbyte.EmptyAirbyteSource;
import io.airbyte.workers.protocols.airbyte.NamespacingMapper;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.nio.file.Path;
import java.time.Duration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@WorkflowInterface
public interface SyncWorkflow {

  @WorkflowMethod
  JobOutput run(long jobId, long attemptId, String sourceDockerImage, String destinationDockerImage, StandardSyncInput syncInput)
      throws TemporalJobException;

  class WorkflowImpl implements SyncWorkflow {

    final ActivityOptions options = ActivityOptions.newBuilder()
        .setScheduleToCloseTimeout(Duration.ofDays(3))
        .build();
    private final SyncActivity activity = Workflow.newActivityStub(SyncActivity.class, options);

    @Override
    public JobOutput run(long jobId, long attemptId, String sourceDockerImage, String destinationDockerImage, StandardSyncInput syncInput)
        throws TemporalJobException {
      return activity.run(jobId, attemptId, sourceDockerImage, destinationDockerImage, syncInput);
    }

  }

  @ActivityInterface
  interface SyncActivity {

    @ActivityMethod
    JobOutput run(long jobId, long attemptId, String sourceDockerImage, String destinationDockerImage, StandardSyncInput syncInput)
        throws TemporalJobException;

  }

  class SyncActivityImpl implements SyncActivity {

    private static final Logger LOGGER = LoggerFactory.getLogger(SyncActivityImpl.class);

    private final ProcessBuilderFactory pbf;
    private final Path workspaceRoot;

    public SyncActivityImpl(ProcessBuilderFactory pbf, Path workspaceRoot) {
      this.pbf = pbf;
      this.workspaceRoot = workspaceRoot;
    }

    public JobOutput run(long jobId, long attemptId, String sourceDockerImage, String destinationDockerImage, StandardSyncInput syncInput) {
      try {
        final Path jobRoot = WorkerUtils.getJobRoot(workspaceRoot, jobId, attemptId);
        WorkerUtils.setJobMdc(jobRoot, jobId);

        final int intAttemptId = Math.toIntExact(attemptId);

        final IntegrationLauncher sourceLauncher = new AirbyteIntegrationLauncher(jobId, intAttemptId, sourceDockerImage, pbf);
        final IntegrationLauncher destinationLauncher = new AirbyteIntegrationLauncher(jobId, intAttemptId, destinationDockerImage, pbf);

        // reset jobs use an empty source to induce resetting all data in destination.
        final AirbyteSource airbyteSource = sourceDockerImage.equals(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB) ? new EmptyAirbyteSource()
            : new DefaultAirbyteSource(sourceLauncher);

        final OutputAndStatus<StandardSyncOutput> run = new DefaultSyncWorker(
            jobId,
            intAttemptId,
            airbyteSource,
            new NamespacingMapper(syncInput.getPrefix()),
            new DefaultAirbyteDestination(destinationLauncher),
            new AirbyteMessageTracker(),
            NormalizationRunnerFactory.create(
                destinationDockerImage,
                pbf,
                syncInput.getDestinationConfiguration())).run(syncInput, jobRoot);
        if (run.getStatus() == JobStatus.SUCCEEDED) {
          Preconditions.checkState(run.getOutput().isPresent());
          LOGGER.info("job output {}", run.getOutput().get());
          return new JobOutput().withSync(run.getOutput().get());
        } else {
          throw new RuntimeException("Sync worker completed with a FAILED status.");
        }

      } catch (Exception e) {
        throw new RuntimeException("Sync job failed with an exception", e);
      }
    }

  }

}
