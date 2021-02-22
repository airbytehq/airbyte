package io.airbyte.scheduler.temporal;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.WorkerRunFactory;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.WorkerConstants;
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

import java.io.File;
import java.io.InputStream;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

import static io.airbyte.workers.JobStatus.FAILED;
import static io.airbyte.workers.JobStatus.SUCCEEDED;

@WorkflowInterface
public interface CheckConnectionWorkflow {
    @WorkflowMethod
    StandardCheckConnectionOutput.Status run(JsonNode connectionConfiguration, String dockerImage);

    class WorkflowImpl implements CheckConnectionWorkflow {
        ActivityOptions options = ActivityOptions.newBuilder()
                .setScheduleToCloseTimeout(Duration.ofMinutes(2)) // todo
                .build();

        private final CheckConnectionActivity activity = Workflow.newActivityStub(CheckConnectionActivity.class, options);

        @Override
        public StandardCheckConnectionOutput.Status run(JsonNode connectionConfiguration, String dockerImage) {
            return activity.run(connectionConfiguration, dockerImage);
        }
    }

    @ActivityInterface
    interface CheckConnectionActivity {
        @ActivityMethod
        StandardCheckConnectionOutput.Status run(JsonNode connectionConfiguration, String dockerImage);
    }

    class CheckConnectionActivityImpl implements CheckConnectionActivity {
        private static final Logger LOGGER = LoggerFactory.getLogger(CheckConnectionActivityImpl.class);

        private final ProcessBuilderFactory pbf;
        private final Path workspaceRoot;

        public CheckConnectionActivityImpl(ProcessBuilderFactory pbf, Path workspaceRoot) {
            this.pbf = pbf;
            this.workspaceRoot = workspaceRoot;
        }

        public StandardCheckConnectionOutput.Status run(JsonNode connectionConfiguration, String dockerImage) {
            try {
                final Path jobRoot = workspaceRoot
                        .resolve("check")
                        .resolve(dockerImage.replaceAll("[^A-Za-z0-9]", ""))
                        .resolve(String.valueOf(Instant.now().getEpochSecond()));

                jobRoot.toFile().mkdirs();
                IOs.writeFile(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME, Jsons.serialize(connectionConfiguration));

                IntegrationLauncher integrationLauncher = WorkerRunFactory.createLauncher(pbf, 0L, 0, dockerImage);

                Process process = integrationLauncher.check(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME).start();

                LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

                AirbyteStreamFactory streamFactory = new DefaultAirbyteStreamFactory();

                Optional<AirbyteConnectionStatus> status;
                try (InputStream stdout = process.getInputStream()) {
                    status = streamFactory.create(IOs.newBufferedReader(stdout))
                            .filter(message -> message.getType() == AirbyteMessage.Type.CONNECTION_STATUS)
                            .map(AirbyteMessage::getConnectionStatus).findFirst();

                    WorkerUtils.gentleClose(process, 1, TimeUnit.MINUTES);
                }

                int exitCode = process.exitValue();

                if (exitCode == 0) {
                    if (status.isEmpty()) {
                        throw new RuntimeException("Check connection job failed to output a status: " + status.get().getMessage());
                    } else {
                        return Enums.convertTo(status.get().getStatus(), StandardCheckConnectionOutput.Status.class);
                    }
                } else {
                    throw new RuntimeException(String.format("Check connection job subprocess finished with exit code {}", exitCode));
                }
            } catch (Exception e) {
                throw new RuntimeException("Check connection job failed with an exception", e);
            }
        }
    }
}
