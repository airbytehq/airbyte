/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.client;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.client.generated.AttemptApi;
import io.airbyte.api.client.generated.ConnectionApi;
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
 * <p>
 * ApiClient.java, FirstApi.java, SecondApi.java
 * <p>
 * To call the API type-safely, we'd do new FirstApi(new ApiClient()).get() or new SecondApi(new
 * ApiClient()).get(), which can get cumbersome if we're interacting with many pieces of the API.
 * <p>
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

  public AttemptApi getAttemptApi() {
    return attemptApi;
  }

  public StateApi getStateApi() {
    return stateApi;
  }

  /**
   * Default to 4 retries with a randomised 1 - 10 seconds interval between the first two retries and
   * an 10-minute wait for the last retry.
   */
  public static <T> T retryWithJitter(final Callable<T> call, final String desc) {
    return retryWithJitter(call, desc, DEFAULT_RETRY_INTERVAL_SECS, DEFAULT_FINAL_INTERVAL_SECS, DEFAULT_MAX_RETRIES);
  }

  /**
   * Provides a simple retry wrapper for api calls. This retry behaviour is slightly different from
   * generally available retries libraries - the last retry is able to wait an interval inconsistent
   * with regular intervals/exponential backoff.
   * <p>
   * Since the primary retries use case is long-running workflows, the benefit of waiting a couple of
   * minutes as a last ditch effort to outlast networking disruption outweighs the cost of slightly
   * longer jobs.
   *
   * @param call method to execute
   * @param desc short readable explanation of why this method is executed
   * @param jitterMaxIntervalSecs upper limit of the randomised retry interval. Minimum value is 1.
   * @param finalIntervalSecs retry interval before the last retry.
   */
  @VisibleForTesting
  // This is okay since we are logging the stack trace, which PMD is not detecting.
  @SuppressWarnings("PMD.PreserveStackTrace")
  public static <T> T retryWithJitter(final Callable<T> call,
                                      final String desc,
                                      final int jitterMaxIntervalSecs,
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

        // Sleep anywhere from 1 to jitterMaxIntervalSecs seconds.
        final var backoffTimeSecs = Math.max(RANDOM.nextInt(jitterMaxIntervalSecs + 1), 1);
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
