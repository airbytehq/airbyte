import io.dataline.api.client.ConnectionApi;
import io.dataline.api.client.DestinationApi;
import io.dataline.api.client.DestinationImplementationApi;
import io.dataline.api.client.DestinationSpecificationApi;
import io.dataline.api.client.JobsApi;
import io.dataline.api.client.SourceApi;
import io.dataline.api.client.SourceImplementationApi;
import io.dataline.api.client.SourceSpecificationApi;
import io.dataline.api.client.WorkspaceApi;
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
