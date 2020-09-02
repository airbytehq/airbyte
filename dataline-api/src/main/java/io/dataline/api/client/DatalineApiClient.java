/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.api.client;

import io.dataline.api.client.invoker.ApiClient;

public class DatalineApiClient {

  private final ConnectionApi connectionApi;
  private final DestinationApi destinationApi;
  private final DestinationImplementationApi destinationImplementationApi;
  private final DestinationSpecificationApi destinationSpecificationApi;
  private final JobsApi jobsApi;
  private final SourceApi sourceApi;
  private final SourceImplementationApi sourceImplementationApi;
  private final SourceSpecificationApi sourceSpecificationApi;
  private final WorkspaceApi workspaceApi;

  public DatalineApiClient(ApiClient apiClient) {
    connectionApi = new ConnectionApi(apiClient);
    destinationApi = new DestinationApi(apiClient);
    destinationImplementationApi = new DestinationImplementationApi(apiClient);
    destinationSpecificationApi = new DestinationSpecificationApi(apiClient);
    jobsApi = new JobsApi(apiClient);
    sourceApi = new SourceApi(apiClient);
    sourceImplementationApi = new SourceImplementationApi(apiClient);
    sourceSpecificationApi = new SourceSpecificationApi(apiClient);
    workspaceApi = new WorkspaceApi(apiClient);
  }

  public ConnectionApi getConnectionApi() {
    return connectionApi;
  }

  public DestinationApi getDestinationApi() {
    return destinationApi;
  }

  public DestinationImplementationApi getDestinationImplementationApi() {
    return destinationImplementationApi;
  }

  public DestinationSpecificationApi getDestinationSpecificationApi() {
    return destinationSpecificationApi;
  }

  public JobsApi getJobsApi() {
    return jobsApi;
  }

  public SourceApi getSourceApi() {
    return sourceApi;
  }

  public SourceImplementationApi getSourceImplementationApi() {
    return sourceImplementationApi;
  }

  public SourceSpecificationApi getSourceSpecificationApi() {
    return sourceSpecificationApi;
  }

  public WorkspaceApi getWorkspaceApi() {
    return workspaceApi;
  }

}
