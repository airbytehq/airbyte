package io.airbyte.server.helpers;

import com.fasterxml.jackson.databind.jsonschema.JsonSchema;
import com.google.common.base.Preconditions;
import com.google.common.cache.CacheBuilder;
import com.google.common.cache.CacheLoader;
import com.google.common.cache.LoadingCache;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.config.JobConfig;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.server.handlers.ConnectionsHandler;
import io.airbyte.server.handlers.DestinationHandler;
import io.airbyte.server.handlers.SourceHandler;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import org.apache.commons.lang3.NotImplementedException;

import java.io.IOException;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;

public class WorkspaceHelper {

    private final ConnectionsHandler connectionsHandler;
    private final SourceHandler sourceHandler;
    private final DestinationHandler destinationHandler;

    private final  LoadingCache<UUID, UUID> sourceToWorkspaceCache;
    private final  LoadingCache<UUID, UUID> destinationToWorkspaceCache;
    private final  LoadingCache<UUID, UUID> connectionToWorkspaceCache;
    private final  LoadingCache<Long, UUID> jobToWorkspaceCache;

    public WorkspaceHelper(ConfigRepository configRepository, JobPersistence jobPersistence, JsonSchemaValidator jsonSchemaValidator, SpecFetcher specFetcher) {
        this.connectionsHandler = new ConnectionsHandler(configRepository);
        this.sourceHandler = new SourceHandler(configRepository, jsonSchemaValidator, specFetcher, connectionsHandler);
        this.destinationHandler = new DestinationHandler(configRepository, jsonSchemaValidator, specFetcher, connectionsHandler);

        this.sourceToWorkspaceCache = getExpiringCache(new CacheLoader<>() {
            @Override
            public UUID load(UUID sourceId) throws JsonValidationException, ConfigNotFoundException, IOException {
                final SourceRead source = sourceHandler.getSource(new SourceIdRequestBody().sourceId(sourceId));
                return source.getWorkspaceId();
            }
        });

        this.destinationToWorkspaceCache = getExpiringCache(new CacheLoader<>() {
            @Override
            public UUID load(UUID destinationId) throws JsonValidationException, ConfigNotFoundException, IOException {
                final DestinationRead destination = destinationHandler.getDestination(new DestinationIdRequestBody().destinationId(destinationId));
                return destination.getWorkspaceId();
            }
        });

        this.connectionToWorkspaceCache = getExpiringCache(new CacheLoader<>() {
            @Override
            public UUID load(UUID connectionId) throws JsonValidationException, ConfigNotFoundException, IOException, ExecutionException {
                final ConnectionRead connection = connectionsHandler.getConnection(new ConnectionIdRequestBody().connectionId(connectionId));
                final UUID sourceId = connection.getSourceId();
                final UUID destinationId = connection.getDestinationId();
                return getWorkspaceForConnection(sourceId, destinationId);
            }
        });

        this.jobToWorkspaceCache = getExpiringCache(new CacheLoader<>() {
            @Override
            public UUID load(Long jobId) throws IOException, ExecutionException {
                final Job job = jobPersistence.getJob(jobId);
                if(job.getConfigType() == JobConfig.ConfigType.SYNC || job.getConfigType() == JobConfig.ConfigType.RESET_CONNECTION) {
                    return getWorkspaceForConnectionId(UUID.fromString(job.getScope()));
                } else {
                    throw new IllegalArgumentException("Only sync/reset jobs are associated with workspaces! A " + job.getConfigType() + " job was requested!");
                }
            }
        });
    }

    public UUID getWorkspaceForSourceId(UUID sourceId) throws ExecutionException {
        return sourceToWorkspaceCache.get(sourceId);
    }

    public UUID getWorkspaceForDestinationId(UUID destinationId) throws ExecutionException {
        return destinationToWorkspaceCache.get(destinationId);
    }

    public UUID getWorkspaceForJobId(Long jobId) throws IOException, ExecutionException {
        return jobToWorkspaceCache.get(jobId);
    }

    public UUID getWorkspaceForConnection(UUID sourceId, UUID destinationId) throws ExecutionException {
        final UUID sourceWorkspace = getWorkspaceForSourceId(sourceId);
        final UUID destinationWorkspace = getWorkspaceForDestinationId(destinationId);

        Preconditions.checkArgument(Objects.equals(sourceWorkspace, destinationWorkspace), "Source and destination must be from the same workspace!");
        return sourceWorkspace;
    }

    public UUID getWorkspaceForConnectionId(UUID connectionId) throws ExecutionException {
        return connectionToWorkspaceCache.get(connectionId);
    }

    public UUID getWorkspaceForOperationId(UUID operationId) {
        throw new NotImplementedException();
    }

    private static <K, V> LoadingCache<K, V> getExpiringCache(CacheLoader<K, V> cacheLoader) {
        return CacheBuilder.newBuilder()
                .expireAfterAccess(5, TimeUnit.MINUTES)
                .build(cacheLoader);
    }

}