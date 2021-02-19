package io.airbyte.scheduler.temporal;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Charsets;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.concurrency.LifecycledCallable;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobSubmitter;
import io.airbyte.scheduler.WorkerRun;
import io.airbyte.scheduler.WorkerRunFactory;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.process.ProcessBuilderFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

public class JobActivityImpl implements  JobActivity{
    private static final Logger LOGGER = LoggerFactory.getLogger(JobActivityImpl.class);

    private final WorkerRunFactory workerRunFactory;
    private final ConfigRepository configRepository;
    private final JobPersistence persistence;

    public JobActivityImpl(WorkerRunFactory workerRunFactory, ConfigRepository configRepository, JobPersistence persistence) {
        this.workerRunFactory = workerRunFactory;
        this.configRepository = configRepository;
        this.persistence = persistence;
    }

    @Override
    public void run(Job job) {
        // we need to know the attempt number before we begin the job lifecycle. thus we state what the
        // attempt number should be. if it is not, that the lifecycle will fail. this should not happen as
        // long as job submission for a single job is single threaded. this is a compromise to allow the job
        // persistence to control what the attempt number should be while still allowing us to declare it
        // before the lifecycle begins.
        final int attemptNumber = job.getAttempts().size();

        try {
            final WorkerRun workerRun = workerRunFactory.create(job);

            final Path logFilePath = workerRun.getJobRoot().resolve(WorkerConstants.LOG_FILENAME);
            final long persistedAttemptId = persistence.createAttempt(job.getId(), logFilePath);
            assertSameIds(attemptNumber, persistedAttemptId);

            MDC.put("job_id", String.valueOf(job.getId()));
            MDC.put("job_root", logFilePath.getParent().toString());
            MDC.put("job_log_filename", logFilePath.getFileName().toString());

            OutputAndStatus<JobOutput> output = workerRun.call();
            if (output.getOutput().isPresent()) {
                persistence.writeOutput(job.getId(), attemptNumber, output.getOutput().get());
            }

            if (output.getStatus() == io.airbyte.workers.JobStatus.SUCCEEDED) {
                persistence.succeedAttempt(job.getId(), attemptNumber);
            } else {
                persistence.failAttempt(job.getId(), attemptNumber);
            }
            trackCompletion(job, output.getStatus());
        } catch (Exception e) {
            try {
                LOGGER.error("Exception thrown in Job Submission: ", e);
                persistence.failAttempt(job.getId(), attemptNumber);
            } catch (IOException ioException) {
                throw new RuntimeException(e);
            } finally {
                trackCompletion(job, io.airbyte.workers.JobStatus.FAILED);
            }
        }

        MDC.clear();
    }

    @VisibleForTesting
    void trackCompletion(Job job, io.airbyte.workers.JobStatus status) {
        try {
            // if there is no scope, do not track. this is the case where we are running check for sources /
            // destinations that don't exist.
            if (Strings.isNullOrEmpty(job.getScope())) {
                return;
            }
            final ImmutableMap.Builder<String, Object> metadataBuilder = generateMetadata(job);
            metadataBuilder.put("attempt_stage", "ENDED");
            metadataBuilder.put("attempt_completion_status", status);
            track(metadataBuilder.build());
        } catch (Exception e) {
            LOGGER.error("failed while reporting usage.", e);
        }
    }

    private void track(Map<String, Object> metadata) {
        // do not track get spec. it is done frequently and not terribly interesting.
        if (metadata.get("job_type").equals("GET_SPEC")) {
            return;
        }

        TrackingClientSingleton.get().track("Connector Jobs", metadata);
    }

    private ImmutableMap.Builder<String, Object> generateMetadata(Job job) throws ConfigNotFoundException, IOException, JsonValidationException {
        final ImmutableMap.Builder<String, Object> metadata = ImmutableMap.builder();
        metadata.put("job_type", job.getConfig().getConfigType());
        metadata.put("job_id", job.getId());
        metadata.put("attempt_id", job.getAttempts());
        // build deterministic job and attempt uuids based off of the scope,which should be unique across
        // all instances of airbyte installed everywhere).
        final UUID jobUuid = UUID.nameUUIDFromBytes((job.getScope() + job.getId() + job.getAttempts()).getBytes(Charsets.UTF_8));
        final UUID attemptUuid = UUID.nameUUIDFromBytes((job.getScope() + job.getId() + job.getAttempts()).getBytes(Charsets.UTF_8));
        metadata.put("job_uuid", jobUuid);
        metadata.put("attempt_uuid", attemptUuid);

        switch (job.getConfig().getConfigType()) {
            case CHECK_CONNECTION_SOURCE, DISCOVER_SCHEMA -> {
                final StandardSourceDefinition sourceDefinition = configRepository.getSourceDefinitionFromSource(UUID.fromString(job.getScope()));

                metadata.put("connector_source", sourceDefinition.getName());
                metadata.put("connector_source_definition_id", sourceDefinition.getSourceDefinitionId());
            }
            case CHECK_CONNECTION_DESTINATION -> {
                final StandardDestinationDefinition destinationDefinition = configRepository
                        .getDestinationDefinitionFromDestination(UUID.fromString(job.getScope()));

                metadata.put("connector_destination", destinationDefinition.getName());
                metadata.put("connector_destination_definition_id", destinationDefinition.getDestinationDefinitionId());
            }
            case GET_SPEC -> {
                // no op because this will be noisy as heck.
            }
            case SYNC -> {
                final UUID connectionId = UUID.fromString(job.getScope());
                final StandardSyncSchedule schedule = configRepository.getStandardSyncSchedule(connectionId);
                final StandardSourceDefinition sourceDefinition = configRepository
                        .getSourceDefinitionFromConnection(connectionId);
                final StandardDestinationDefinition destinationDefinition = configRepository
                        .getDestinationDefinitionFromConnection(connectionId);

                metadata.put("connection_id", connectionId);
                metadata.put("connector_source", sourceDefinition.getName());
                metadata.put("connector_source_definition_id", sourceDefinition.getSourceDefinitionId());
                metadata.put("connector_destination", destinationDefinition.getName());
                metadata.put("connector_destination_definition_id", destinationDefinition.getDestinationDefinitionId());

                String frequencyString;
                if (schedule.getManual()) {
                    frequencyString = "manual";
                } else {
                    final long intervalInMinutes = TimeUnit.SECONDS.toMinutes(ScheduleHelpers.getIntervalInSecond(schedule.getSchedule()));
                    frequencyString = intervalInMinutes + " min";
                }
                metadata.put("frequency", frequencyString);
            }
        }
        return metadata;
    }

    private static void assertSameIds(long expectedAttemptId, long actualAttemptId) {
        if (expectedAttemptId != actualAttemptId) {
            throw new IllegalStateException("Created attempt was not the expected attempt");
        }
    }
}
