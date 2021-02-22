package io.airbyte.scheduler.temporal;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.WorkerRunFactory;
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

import java.io.InputStream;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

@WorkflowInterface
public interface DiscoverWorkflow {
    @WorkflowMethod
    AirbyteCatalog run(JsonNode connectionConfiguration, String dockerImage);

    class WorkflowImpl implements DiscoverWorkflow {
        ActivityOptions options = ActivityOptions.newBuilder()
                .setScheduleToCloseTimeout(Duration.ofMinutes(2)) // todo
                .build();

        private final DiscoverActivity activity = Workflow.newActivityStub(DiscoverActivity.class, options);

        @Override
        public AirbyteCatalog run(JsonNode connectionConfiguration, String dockerImage) {
            return activity.run(connectionConfiguration, dockerImage);
        }
    }

    @ActivityInterface
    interface DiscoverActivity {
        @ActivityMethod
        AirbyteCatalog run(JsonNode connectionConfiguration, String dockerImage);
    }

    class DiscoverActivityImpl implements DiscoverActivity {
        private static final Logger LOGGER = LoggerFactory.getLogger(DiscoverActivityImpl.class);

        private final ProcessBuilderFactory pbf;
        private final Path workspaceRoot;

        public DiscoverActivityImpl(ProcessBuilderFactory pbf, Path workspaceRoot) {
            this.pbf = pbf;
            this.workspaceRoot = workspaceRoot;
        }

        public AirbyteCatalog run(JsonNode connectionConfiguration, String dockerImage) {
            try {
                final Path jobRoot = workspaceRoot
                        .resolve("discover")
                        .resolve(dockerImage.replaceAll("[^A-Za-z0-9]", ""))
                        .resolve(String.valueOf(Instant.now().getEpochSecond()));

                jobRoot.toFile().mkdirs();
                IOs.writeFile(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME, Jsons.serialize(connectionConfiguration));

                IntegrationLauncher integrationLauncher = WorkerRunFactory.createLauncher(pbf, 0L, 0, dockerImage);

                Process process = integrationLauncher.discover(jobRoot, WorkerConstants.TAP_CONFIG_JSON_FILENAME)
                        .start();

                LineGobbler.gobble(process.getErrorStream(), LOGGER::error);

                AirbyteStreamFactory streamFactory = new DefaultAirbyteStreamFactory();

                Optional<AirbyteCatalog> catalog;
                try (InputStream stdout = process.getInputStream()) {
                    catalog = streamFactory.create(IOs.newBufferedReader(stdout))
                            .filter(message -> message.getType() == AirbyteMessage.Type.CATALOG)
                            .map(AirbyteMessage::getCatalog)
                            .findFirst();

                    WorkerUtils.gentleClose(process, 30, TimeUnit.MINUTES);
                }

                int exitCode = process.exitValue();
                if (exitCode == 0) {
                    if (catalog.isEmpty()) {
                        throw new RuntimeException("Discover job failed to output a catalog.");
                    } else {
                        return catalog.get();
                    }
                } else {
                    throw new RuntimeException(String.format("Discover job subprocess finished with exit code {}", exitCode));
                }
            } catch (Exception e) {
                throw new RuntimeException("Discover job failed with an exception", e);
            }
        }
    }
}
