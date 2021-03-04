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

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.config.IntegrationLauncherConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteStreamFactory;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteStreamFactory;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.io.InputStream;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@WorkflowInterface
public interface SpecWorkflow {

  @WorkflowMethod
  ConnectorSpecification run(IntegrationLauncherConfig launcherConfig);

  class WorkflowImpl implements SpecWorkflow {

    ActivityOptions options = ActivityOptions.newBuilder()
        .setScheduleToCloseTimeout(Duration.ofMinutes(2)) // todo
        .build();

    private final SpecActivity activity = Workflow.newActivityStub(SpecActivity.class, options);

    @Override
    public ConnectorSpecification run(IntegrationLauncherConfig launcherConfig) {
      return activity.run(launcherConfig);
    }

  }

  @ActivityInterface
  interface SpecActivity {

    @ActivityMethod
    ConnectorSpecification run(IntegrationLauncherConfig launcherConfig);

  }

  class SpecActivityImpl implements SpecActivity {

    private static final Logger LOGGER = LoggerFactory.getLogger(SpecActivityImpl.class);

    private final ProcessBuilderFactory pbf;
    private final Path workspaceRoot;

    public SpecActivityImpl(ProcessBuilderFactory pbf, Path workspaceRoot) {
      this.pbf = pbf;
      this.workspaceRoot = workspaceRoot;
    }

    public ConnectorSpecification run(IntegrationLauncherConfig launcherConfig) {
      try {
        // todo (cgardens) - we need to find a way to standardize log paths sanely across all workflow.
        // right now we have this in temporal workflow.
        final Path jobRoot = workspaceRoot
            .resolve("spec")
            .resolve(launcherConfig.getDockerImage().replaceAll("[^A-Za-z0-9]", ""))
            .resolve(String.valueOf(Instant.now().getEpochSecond()));

        final IntegrationLauncher integrationLauncher =
            new AirbyteIntegrationLauncher(launcherConfig.getJobId(), launcherConfig.getAttemptId().intValue(), launcherConfig.getDockerImage(), pbf);
        final Process process = integrationLauncher.spec(jobRoot).start();

        LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

        final AirbyteStreamFactory streamFactory = new DefaultAirbyteStreamFactory();

        Optional<ConnectorSpecification> spec;
        try (InputStream stdout = process.getInputStream()) {
          spec = streamFactory.create(IOs.newBufferedReader(stdout))
              .filter(message -> message.getType() == AirbyteMessage.Type.SPEC)
              .map(AirbyteMessage::getSpec)
              .findFirst();

          // todo (cgardens) - let's pre-fetch the images outside of the worker so we don't need account for
          // this.
          // retrieving spec should generally be instantaneous, but since docker images might not be pulled
          // it could take a while longer depending on internet conditions as well.
          WorkerUtils.gentleClose(process, 30, TimeUnit.MINUTES);
        }

        int exitCode = process.exitValue();
        if (exitCode == 0) {
          if (spec.isEmpty()) {
            throw new RuntimeException("Spec job failed to output a spec struct.");
          } else {
            return spec.get();
          }
        } else {
          throw new RuntimeException(String.format("Spec job subprocess finished with exit code %s", exitCode));
        }
      } catch (Exception e) {
        throw new RuntimeException("Spec job failed with an exception", e);
      }
    }

  }

}
