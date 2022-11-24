/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.client;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.client.generated.AttemptApi;
import io.airbyte.api.client.generated.ConnectionApi;
import io.airbyte.api.client.generated.DbMigrationApi;
import io.airbyte.api.client.generated.DestinationApi;
import io.airbyte.api.client.generated.DestinationDefinitionApi;
import io.airbyte.api.client.generated.DestinationDefinitionSpecificationApi;
import io.airbyte.api.client.generated.HealthApi;
import io.airbyte.api.client.generated.JobsApi;
import io.airbyte.api.client.generated.OperationApi;
import io.airbyte.api.client.generated.SourceApi;
import io.airbyte.api.client.generated.SourceDefinitionApi;
import io.airbyte.api.client.generated.SourceDefinitionSpecificationApi;
import io.airbyte.api.client.generated.StateApi;
import io.airbyte.api.client.generated.WorkspaceApi;
import io.airbyte.api.client.invoker.generated.ApiClient;
import java.util.Random;
import java.util.concurrent.Callable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is meant to consolidate all our API endpoints into a fluent-ish client. Currently, all
 * open API generators create a separate class per API "root-route". For example, if our API has two
 * routes "/v1/First/get" and "/v1/Second/get", OpenAPI generates (essentially) the following files:
 *
 * ApiClient.java, FirstApi.java, SecondApi.java
 *
 * To call the API type-safely, we'd do new FirstApi(new ApiClient()).get() or new SecondApi(new
 * ApiClient()).get(), which can get cumbersome if we're interacting with many pieces of the API.
 *
 * This is currently manually maintained. We could look into autogenerating it if needed.
 */
public class AirbyteApiClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteApiClient.class);
  private static final Random RANDOM = new Random();

  public static final int DEFAULT_MAX_RETRIES = 4;
  public static final int DEFAULT_RETRY_INTERVAL_SECS = 10;

  public static final int DEFAULT_FINAL_INTERVAL_SECS = 10 * 60;

  private final ConnectionApi connectionApi;
  private final DestinationDefinitionApi destinationDefinitionApi;
  private final DestinationApi destinationApi;
  private final DestinationDefinitionSpecificationApi destinationSpecificationApi;
  private final JobsApi jobsApi;
  private final PatchedLogsApi logsApi;
  private final OperationApi operationApi;
  private final SourceDefinitionApi sourceDefinitionApi;
  private final SourceApi sourceApi;
  private final SourceDefinitionSpecificationApi sourceDefinitionSpecificationApi;
  private final WorkspaceApi workspaceApi;
  private final HealthApi healthApi;
  private final DbMigrationApi dbMigrationApi;
  private final AttemptApi attemptApi;
  private final StateApi stateApi;

  public AirbyteApiClient(final ApiClient apiClient) {
    connectionApi = new ConnectionApi(apiClient);
    destinationDefinitionApi = new DestinationDefinitionApi(apiClient);
    destinationApi = new DestinationApi(apiClient);
    destinationSpecificationApi = new DestinationDefinitionSpecificationApi(apiClient);
    jobsApi = new JobsApi(apiClient);
    logsApi = new PatchedLogsApi(apiClient);
    operationApi = new OperationApi(apiClient);
    sourceDefinitionApi = new SourceDefinitionApi(apiClient);
    sourceApi = new SourceApi(apiClient);
    sourceDefinitionSpecificationApi = new SourceDefinitionSpecificationApi(apiClient);
    workspaceApi = new WorkspaceApi(apiClient);
    healthApi = new HealthApi(apiClient);
    dbMigrationApi = new DbMigrationApi(apiClient);
    attemptApi = new AttemptApi(apiClient);
    stateApi = new StateApi(apiClient);
  }

  public ConnectionApi getConnectionApi() {
    return connectionApi;
  }

  public DestinationDefinitionApi getDestinationDefinitionApi() {
    return destinationDefinitionApi;
  }

  public DestinationApi getDestinationApi() {
    return destinationApi;
  }

  public DestinationDefinitionSpecificationApi getDestinationDefinitionSpecificationApi() {
    return destinationSpecificationApi;
  }

  public JobsApi getJobsApi() {
    return jobsApi;
  }

  public SourceDefinitionApi getSourceDefinitionApi() {
    return sourceDefinitionApi;
  }

  public SourceApi getSourceApi() {
    return sourceApi;
  }

  public SourceDefinitionSpecificationApi getSourceDefinitionSpecificationApi() {
    return sourceDefinitionSpecificationApi;
  }

  public WorkspaceApi getWorkspaceApi() {
    return workspaceApi;
  }

  public PatchedLogsApi getLogsApi() {
    return logsApi;
  }

  public OperationApi getOperationApi() {
    return operationApi;
  }

  public HealthApi getHealthApi() {
    return healthApi;
  }

  public DbMigrationApi getDbMigrationApi() {
    return dbMigrationApi;
  }

  public AttemptApi getAttemptApi() {
    return attemptApi;
  }

  public StateApi getStateApi() {
    return stateApi;
  }

  public static <T> T retryWithJitter(final Callable<T> call, final String desc) {
    return retryWithJitter(call, desc, DEFAULT_RETRY_INTERVAL_SECS, DEFAULT_FINAL_INTERVAL_SECS, DEFAULT_MAX_RETRIES);
  }

  @VisibleForTesting
  @SuppressWarnings("PMD.PreserveStackTrace")
  public static <T> T retryWithJitter(final Callable<T> call,
                                      final String desc,
                                      final int jitterIntervalSecs,
                                      final int finalIntervalSecs,
                                      final int maxTries) {
    int currRetries = 0;
    boolean keepTrying = true;

    T data = null;
    while (keepTrying && currRetries < maxTries) {
      try {
        LOGGER.info("Attempt {} to {}", currRetries, desc);
        data = call.call();

        keepTrying = false;
      } catch (final Exception e) {
        LOGGER.info("Attempt {} to {} error: {}", currRetries, desc, e);
        currRetries++;

        // Sleep anywhere from 1 to jitterIntervalSecs seconds.
        final var backoffTimeSecs = Math.min(RANDOM.nextInt(jitterIntervalSecs + 1), 1);
        var backoffTimeMs = backoffTimeSecs * 1000;

        if (currRetries == maxTries - 1) {
          // sleep for finalIntervalMins on the last attempt.
          backoffTimeMs = finalIntervalSecs * 1000;
        }

        try {
          Thread.sleep(backoffTimeMs);
        } catch (final InterruptedException ex) {
          throw new RuntimeException(ex);
        }
      }
    }
    return data;
  }

}
