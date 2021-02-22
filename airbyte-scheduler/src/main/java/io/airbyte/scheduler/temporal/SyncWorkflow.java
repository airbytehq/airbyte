package io.airbyte.scheduler.temporal;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardTapConfig;
import io.airbyte.config.StandardTargetConfig;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.scheduler.WorkerRunFactory;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.normalization.NormalizationRunner;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteDestination;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageTracker;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.AirbyteStreamFactory;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteDestination;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
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
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@WorkflowInterface
public interface SyncWorkflow {
    @WorkflowMethod
    void run(StandardSyncInput syncInput, String sourceDockerImage, String destinationDockerImage);

    class WorkflowImpl implements SyncWorkflow {
        ActivityOptions options = ActivityOptions.newBuilder()
                .setScheduleToCloseTimeout(Duration.ofMinutes(2)) // todo
                .build();

        private final SyncActivity activity = Workflow.newActivityStub(SyncActivity.class, options);

        @Override
        public void run(StandardSyncInput syncInput, String sourceDockerImage, String destinationDockerImage) {
            activity.run(syncInput, sourceDockerImage, destinationDockerImage);
        }
    }

    @ActivityInterface
    interface SyncActivity {
        @ActivityMethod
        void run(StandardSyncInput syncInput, String sourceDockerImage, String destinationDockerImage);
    }

    class SyncActivityImpl implements SyncActivity {
        private static final Logger LOGGER = LoggerFactory.getLogger(SyncActivityImpl.class);

        private final ProcessBuilderFactory pbf;
        private final Path workspaceRoot;

        public SyncActivityImpl(ProcessBuilderFactory pbf, Path workspaceRoot) {
            this.pbf = pbf;
            this.workspaceRoot = workspaceRoot;
        }

        public void run(StandardSyncInput syncInput, String sourceDockerImage, String destinationDockerImage) {
            try {
                final IntegrationLauncher sourceLauncher = WorkerRunFactory.createLauncher(pbf, 0L, 0, sourceDockerImage);
                final IntegrationLauncher destinationLauncher = WorkerRunFactory.createLauncher(pbf, 0L, 0, destinationDockerImage);

                final AirbyteSource source = new DefaultAirbyteSource(sourceLauncher);
                final AirbyteDestination destination = new DefaultAirbyteDestination(destinationLauncher);

                final NormalizationRunner normalizationRunner = NormalizationRunnerFactory.create(
                        destinationDockerImage,
                        pbf,
                        syncInput.getDestinationConfiguration());

                final AirbyteMessageTracker messageTracker = new AirbyteMessageTracker();

                final Path jobRoot = workspaceRoot
                        .resolve("sync")
                        .resolve(String.valueOf(Instant.now().getEpochSecond())); // todo

                jobRoot.toFile().mkdirs();

                long startTime = System.currentTimeMillis();

                LOGGER.info("configured sync modes: {}", syncInput.getCatalog().getStreams()
                        .stream()
                        .collect(Collectors.toMap(s -> s.getStream().getName(), s -> s.getSyncMode() != null ? s.getSyncMode() : SyncMode.FULL_REFRESH)));

                final StandardTapConfig tapConfig = WorkerUtils.syncToTapConfig(syncInput);
                final StandardTargetConfig targetConfig = WorkerUtils.syncToTargetConfig(syncInput);

                try (destination; source) {
                    destination.start(targetConfig, jobRoot);
                    source.start(tapConfig, jobRoot);

                    while (!source.isFinished()) {
                        final Optional<AirbyteMessage> maybeMessage = source.attemptRead();
                        if (maybeMessage.isPresent()) {
                            final AirbyteMessage message = maybeMessage.get();

                            messageTracker.accept(message);
                            destination.accept(message);
                        }
                    }

                } catch (Exception e) {
                    throw new RuntimeException("Sync worker failed.", e);
                }

                try (normalizationRunner) {
                    LOGGER.info("Running normalization.");
                    normalizationRunner.start();
                    final Path normalizationRoot = Files.createDirectories(jobRoot.resolve("normalize"));
                    if (!normalizationRunner.normalize(0L, 0, normalizationRoot, syncInput.getDestinationConfiguration(), syncInput.getCatalog())) {
                        throw new WorkerException("Normalization Failed.");
                    }
                } catch (Exception e) {
                    throw new RuntimeException("Normalization Failed.", e);
                }

                final StandardSyncSummary summary = new StandardSyncSummary()
                        .withStatus(StandardSyncSummary.Status.COMPLETED)
                        .withRecordsSynced(messageTracker.getRecordCount())
                        .withBytesSynced(messageTracker.getBytesCount())
                        .withStartTime(startTime)
                        .withEndTime(System.currentTimeMillis());

                LOGGER.info("sync summary: {}", summary);

                final StandardSyncOutput output = new StandardSyncOutput().withStandardSyncSummary(summary);
                messageTracker.getOutputState().ifPresent(capturedState -> {
                    final State state = new State()
                            .withState(capturedState);
                    output.withState(state);
                });
            } catch (Exception e) {
                throw new RuntimeException("Sync job failed with an exception", e);
            }
        }
    }
}
