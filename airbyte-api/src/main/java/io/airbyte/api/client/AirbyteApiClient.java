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

package io.airbyte.api.client;

import io.airbyte.api.client.invoker.ApiClient;

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

  public AirbyteApiClient(ApiClient apiClient) {
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

}
