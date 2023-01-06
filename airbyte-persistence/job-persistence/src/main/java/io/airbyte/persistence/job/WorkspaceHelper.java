/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job;

import com.google.common.base.Preconditions;
import com.google.common.cache.CacheBuilder;
import com.google.common.cache.CacheLoader;
import com.google.common.cache.LoadingCache;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.validation.json.JsonValidationException;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import org.checkerframework.checker.nullness.qual.NonNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// todo (cgardens) - this class is in an unintuitive module. it is weird that you need to import
// scheduler:persistence in order to get workspace ids for configs (e.g. source). Our options are to
// split this helper by database or put it in a new module.
@SuppressWarnings("PMD.AvoidCatchingThrowable")
@Singleton
public class WorkspaceHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkspaceHelper.class);

  private final LoadingCache<UUID, UUID> sourceToWorkspaceCache;
  private final LoadingCache<UUID, UUID> destinationToWorkspaceCache;
  private final LoadingCache<UUID, UUID> connectionToWorkspaceCache;
  private final LoadingCache<UUID, UUID> operationToWorkspaceCache;
  private final LoadingCache<Long, UUID> jobToWorkspaceCache;

  public WorkspaceHelper(final ConfigRepository configRepository, final JobPersistence jobPersistence) {

    this.sourceToWorkspaceCache = getExpiringCache(new CacheLoader<>() {

      @Override
      public UUID load(@NonNull final UUID sourceId) throws JsonValidationException, ConfigNotFoundException, IOException {
        final SourceConnection source = configRepository.getSourceConnection(sourceId);
        return source.getWorkspaceId();
      }

    });

    this.destinationToWorkspaceCache = getExpiringCache(new CacheLoader<>() {

      @Override
      public UUID load(@NonNull final UUID destinationId) throws JsonValidationException, ConfigNotFoundException, IOException {
        final DestinationConnection destination = configRepository.getDestinationConnection(destinationId);
        return destination.getWorkspaceId();
      }

    });

    this.connectionToWorkspaceCache = getExpiringCache(new CacheLoader<>() {

      @Override
      public UUID load(@NonNull final UUID connectionId) throws JsonValidationException, ConfigNotFoundException, IOException {
        final StandardSync connection = configRepository.getStandardSync(connectionId);
        final UUID sourceId = connection.getSourceId();
        final UUID destinationId = connection.getDestinationId();
        return getWorkspaceForConnectionIgnoreExceptions(sourceId, destinationId);
      }

    });

    this.operationToWorkspaceCache = getExpiringCache(new CacheLoader<>() {

      @Override
      public UUID load(@NonNull final UUID operationId) throws JsonValidationException, ConfigNotFoundException, IOException {
        final StandardSyncOperation operation = configRepository.getStandardSyncOperation(operationId);
        return operation.getWorkspaceId();
      }

    });

    this.jobToWorkspaceCache = getExpiringCache(new CacheLoader<>() {

      @Override
      public UUID load(@NonNull final Long jobId) throws ConfigNotFoundException, IOException {
        final Job job = jobPersistence.getJob(jobId);
        if (job == null) {
          throw new ConfigNotFoundException(Job.class.toString(), jobId.toString());
        }
        if (job.getConfigType() == JobConfig.ConfigType.SYNC || job.getConfigType() == JobConfig.ConfigType.RESET_CONNECTION) {
          return getWorkspaceForConnectionIdIgnoreExceptions(UUID.fromString(job.getScope()));
        } else {
          throw new IllegalArgumentException("Only sync/reset jobs are associated with workspaces! A " + job.getConfigType() + " job was requested!");
        }
      }

    });
  }

  /**
   * There are generally two kinds of helper methods present here. The first kind propagate exceptions
   * for the method backing the cache. The second ignores them. The former is meant to be used with
   * proper api calls, while the latter is meant to be use with asserts and precondtions checks.
   * <p>
   * In API calls, distinguishing between various exceptions helps return the correct status code.
   */

  // SOURCE ID
  public UUID getWorkspaceForSourceId(final UUID sourceId) throws ConfigNotFoundException, JsonValidationException {
    return handleCacheExceptions(() -> sourceToWorkspaceCache.get(sourceId));
  }

  public UUID getWorkspaceForSourceIdIgnoreExceptions(final UUID sourceId) {
    return swallowExecutionException(() -> getWorkspaceForSourceId(sourceId));
  }

  // DESTINATION ID
  public UUID getWorkspaceForDestinationId(final UUID destinationId) throws JsonValidationException, ConfigNotFoundException {
    return handleCacheExceptions(() -> destinationToWorkspaceCache.get(destinationId));
  }

  public UUID getWorkspaceForDestinationIdIgnoreExceptions(final UUID destinationId) {
    return swallowExecutionException(() -> destinationToWorkspaceCache.get(destinationId));
  }

  // JOB ID
  public UUID getWorkspaceForJobId(final Long jobId) throws JsonValidationException, ConfigNotFoundException {
    return handleCacheExceptions(() -> jobToWorkspaceCache.get(jobId));
  }

  public UUID getWorkspaceForJobIdIgnoreExceptions(final Long jobId) {
    return swallowExecutionException(() -> jobToWorkspaceCache.get(jobId));
  }

  // CONNECTION ID
  public UUID getWorkspaceForConnection(final UUID sourceId, final UUID destinationId) throws JsonValidationException, ConfigNotFoundException {
    final UUID sourceWorkspace = getWorkspaceForSourceId(sourceId);
    final UUID destinationWorkspace = getWorkspaceForDestinationId(destinationId);

    Preconditions.checkArgument(Objects.equals(sourceWorkspace, destinationWorkspace), "Source and destination must be from the same workspace!");
    return sourceWorkspace;
  }

  public UUID getWorkspaceForConnectionIgnoreExceptions(final UUID sourceId, final UUID destinationId) {
    final UUID sourceWorkspace = getWorkspaceForSourceIdIgnoreExceptions(sourceId);
    final UUID destinationWorkspace = getWorkspaceForDestinationIdIgnoreExceptions(destinationId);

    Preconditions.checkArgument(Objects.equals(sourceWorkspace, destinationWorkspace), "Source and destination must be from the same workspace!");
    return sourceWorkspace;
  }

  public UUID getWorkspaceForConnectionId(final UUID connectionId) throws JsonValidationException, ConfigNotFoundException {
    return handleCacheExceptions(() -> connectionToWorkspaceCache.get(connectionId));
  }

  public UUID getWorkspaceForConnectionIdIgnoreExceptions(final UUID connectionId) {
    return swallowExecutionException(() -> connectionToWorkspaceCache.get(connectionId));
  }

  // OPERATION ID
  public UUID getWorkspaceForOperationId(final UUID operationId) throws JsonValidationException, ConfigNotFoundException {
    return handleCacheExceptions(() -> operationToWorkspaceCache.get(operationId));
  }

  public UUID getWorkspaceForOperationIdIgnoreExceptions(final UUID operationId) {
    return swallowExecutionException(() -> operationToWorkspaceCache.get(operationId));
  }

  private static UUID handleCacheExceptions(final CheckedSupplier<UUID, ExecutionException> supplier)
      throws ConfigNotFoundException, JsonValidationException {
    try {
      return supplier.get();
    } catch (final ExecutionException e) {
      LOGGER.error("Error retrieving cache:", e.getCause());
      if (e.getCause() instanceof ConfigNotFoundException) {
        throw (ConfigNotFoundException) e.getCause();
      }
      if (e.getCause() instanceof JsonValidationException) {
        throw (JsonValidationException) e.getCause();
      }
      throw new RuntimeException(e.getCause().toString(), e);
    }
  }

  private static UUID swallowExecutionException(final CheckedSupplier<UUID, Throwable> supplier) {
    try {
      return supplier.get();
    } catch (final Throwable e) {
      throw new RuntimeException(e);
    }
  }

  private static <K, V> LoadingCache<K, V> getExpiringCache(final CacheLoader<K, V> cacheLoader) {
    return CacheBuilder.newBuilder()
        .maximumSize(20000)
        .build(cacheLoader);
  }

}
