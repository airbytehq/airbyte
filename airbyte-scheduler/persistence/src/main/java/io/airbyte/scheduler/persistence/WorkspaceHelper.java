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

package io.airbyte.scheduler.persistence;

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
import io.airbyte.scheduler.models.Job;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import org.checkerframework.checker.nullness.qual.NonNull;

// todo (cgardens) - this class is in an unintuitive module. it is weird that you need to import
// scheduler:persistence in order to get workspace ids for configs (e.g. source). Our options are to
// split this helper by database or put it in a new module.
public class WorkspaceHelper {

  private final LoadingCache<UUID, UUID> sourceToWorkspaceCache;
  private final LoadingCache<UUID, UUID> destinationToWorkspaceCache;
  private final LoadingCache<UUID, UUID> connectionToWorkspaceCache;
  private final LoadingCache<UUID, UUID> operationToWorkspaceCache;
  private final LoadingCache<Long, UUID> jobToWorkspaceCache;

  public WorkspaceHelper(ConfigRepository configRepository, JobPersistence jobPersistence) {

    this.sourceToWorkspaceCache = getExpiringCache(new CacheLoader<>() {

      @Override
      public UUID load(@NonNull UUID sourceId) throws JsonValidationException, ConfigNotFoundException, IOException {
        final SourceConnection source = configRepository.getSourceConnection(sourceId);
        return source.getWorkspaceId();
      }

    });

    this.destinationToWorkspaceCache = getExpiringCache(new CacheLoader<>() {

      @Override
      public UUID load(@NonNull UUID destinationId) throws JsonValidationException, ConfigNotFoundException, IOException {
        final DestinationConnection destination = configRepository.getDestinationConnection(destinationId);
        return destination.getWorkspaceId();
      }

    });

    this.connectionToWorkspaceCache = getExpiringCache(new CacheLoader<>() {

      @Override
      public UUID load(@NonNull UUID connectionId) throws JsonValidationException, ConfigNotFoundException, IOException {
        final StandardSync connection = configRepository.getStandardSync(connectionId);
        final UUID sourceId = connection.getSourceId();
        final UUID destinationId = connection.getDestinationId();
        return getWorkspaceForConnection(sourceId, destinationId);
      }

    });

    this.operationToWorkspaceCache = getExpiringCache(new CacheLoader<>() {

      @Override
      public UUID load(@NonNull UUID operationId) throws JsonValidationException, ConfigNotFoundException, IOException {
        final StandardSyncOperation operation = configRepository.getStandardSyncOperation(operationId);
        return operation.getWorkspaceId();
      }

    });

    this.jobToWorkspaceCache = getExpiringCache(new CacheLoader<>() {

      @Override
      public UUID load(@NonNull Long jobId) throws IOException {
        final Job job = jobPersistence.getJob(jobId);
        if (job.getConfigType() == JobConfig.ConfigType.SYNC || job.getConfigType() == JobConfig.ConfigType.RESET_CONNECTION) {
          return getWorkspaceForConnectionId(UUID.fromString(job.getScope()));
        } else {
          throw new IllegalArgumentException("Only sync/reset jobs are associated with workspaces! A " + job.getConfigType() + " job was requested!");
        }
      }

    });
  }

  public UUID getWorkspaceForSourceId(UUID sourceId) {
    return swallowExecutionException(() -> sourceToWorkspaceCache.get(sourceId));
  }

  public UUID getWorkspaceForDestinationId(UUID destinationId) {
    return swallowExecutionException(() -> destinationToWorkspaceCache.get(destinationId));
  }

  public UUID getWorkspaceForJobId(Long jobId) {
    return swallowExecutionException(() -> jobToWorkspaceCache.get(jobId));
  }

  public UUID getWorkspaceForConnection(UUID sourceId, UUID destinationId) {
    final UUID sourceWorkspace = getWorkspaceForSourceId(sourceId);
    final UUID destinationWorkspace = getWorkspaceForDestinationId(destinationId);

    Preconditions.checkArgument(Objects.equals(sourceWorkspace, destinationWorkspace), "Source and destination must be from the same workspace!");
    return swallowExecutionException(() -> sourceWorkspace);
  }

  public UUID getWorkspaceForConnectionId(UUID connectionId) {
    return swallowExecutionException(() -> connectionToWorkspaceCache.get(connectionId));
  }

  public UUID getWorkspaceForOperationId(UUID operationId) {
    return swallowExecutionException(() -> operationToWorkspaceCache.get(operationId));
  }

  // the ExecutionException is an implementation detail the helper and does not need to be handled by
  // callers.
  private static UUID swallowExecutionException(CheckedSupplier<UUID, ExecutionException> supplier) {
    try {
      return supplier.get();
    } catch (ExecutionException e) {
      throw new RuntimeException(e);
    }
  }

  private static <K, V> LoadingCache<K, V> getExpiringCache(CacheLoader<K, V> cacheLoader) {
    return CacheBuilder.newBuilder()
        .maximumSize(20000)
        .build(cacheLoader);
  }

}
