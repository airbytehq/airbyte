package io.airbyte.scheduler.temporal;

import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.WorkerRunFactory;
import io.airbyte.workers.WorkerUtils;
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.InputStream;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

@WorkflowInterface
public interface SpecWorkflow {
    @WorkflowMethod
    ConnectorSpecification run(String dockerImage);

    class WorkflowImpl implements SpecWorkflow {
        ActivityOptions options = ActivityOptions.newBuilder()
                .setScheduleToCloseTimeout(Duration.ofMinutes(2)) // todo
                .build();

        private final SpecActivity activity = Workflow.newActivityStub(SpecActivity.class, options);

        @Override
        public ConnectorSpecification run(String dockerImage) {
            return activity.run(dockerImage);
        }
    }

    @ActivityInterface
    interface SpecActivity {
        @ActivityMethod
        ConnectorSpecification run(String dockerImage);
    }

    class SpecActivityImpl implements SpecActivity {
        private static final Logger LOGGER = LoggerFactory.getLogger(SpecActivityImpl.class);

        private final ProcessBuilderFactory pbf;
        private final Path workspaceRoot;

        public SpecActivityImpl(ProcessBuilderFactory pbf, Path workspaceRoot) {
            this.pbf = pbf;
            this.workspaceRoot = workspaceRoot;
        }

        public ConnectorSpecification run(String dockerImage) {
            try {
                final Path jobRoot = workspaceRoot
                        .resolve("spec")
                        .resolve(dockerImage.replaceAll("[^A-Za-z0-9]", ""))
                        .resolve(String.valueOf(Instant.now().getEpochSecond()));

                IntegrationLauncher integrationLauncher = WorkerRunFactory.createLauncher(pbf, 0L, 0, dockerImage);
                Process process = integrationLauncher.spec(jobRoot).start();

                LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

                AirbyteStreamFactory streamFactory = new DefaultAirbyteStreamFactory();

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
                    throw new RuntimeException(String.format("Spec job subprocess finished with exit code {}", exitCode));
                }
            } catch (Exception e) {
                throw new RuntimeException("Spec job failed with an exception", e);
            }
        }
    }
}
