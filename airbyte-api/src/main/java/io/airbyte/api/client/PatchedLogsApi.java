/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.client;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.invoker.generated.ApiResponse;
import io.airbyte.api.client.model.generated.LogsRequestBody;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.function.Consumer;
import org.apache.commons.io.FileUtils;

/**
 * This class is a copy of {@link io.airbyte.api.client.generated.LogsApi} except it allows Accept:
 * text/plain. Without this modification, {@link io.airbyte.api.client.generated.LogsApi} returns a
 * 406 because the generated code requests the wrong response type.
 */
public class PatchedLogsApi {

  private final HttpClient memberVarHttpClient;
  private final ObjectMapper memberVarObjectMapper;
  private final String memberVarBaseUri;
  private final Consumer<HttpRequest.Builder> memberVarInterceptor;
  private final Duration memberVarReadTimeout;
  private final Consumer<HttpResponse<InputStream>> memberVarResponseInterceptor;

  public PatchedLogsApi() {
    this(new ApiClient());
  }

  public PatchedLogsApi(final ApiClient apiClient) {
    memberVarHttpClient = apiClient.getHttpClient();
    memberVarObjectMapper = apiClient.getObjectMapper();
    memberVarBaseUri = apiClient.getBaseUri();
    memberVarInterceptor = apiClient.getRequestInterceptor();
    memberVarReadTimeout = apiClient.getReadTimeout();
    memberVarResponseInterceptor = apiClient.getResponseInterceptor();
  }

  /**
   * Get logs
   *
   * @param logsRequestBody (required)
   * @return File
   * @throws ApiException if fails to make API call
   */
  public File getLogs(final LogsRequestBody logsRequestBody) throws ApiException {
    final ApiResponse<File> localVarResponse = getLogsWithHttpInfo(logsRequestBody);
    return localVarResponse.getData();
  }

  /**
   * Get logs
   *
   * @param logsRequestBody (required)
   * @return ApiResponse&lt;File&gt;
   * @throws ApiException if fails to make API call
   */
  public ApiResponse<File> getLogsWithHttpInfo(final LogsRequestBody logsRequestBody) throws ApiException {
    final HttpRequest.Builder localVarRequestBuilder = getLogsRequestBuilder(logsRequestBody);
    try {
      final HttpResponse<InputStream> localVarResponse = memberVarHttpClient.send(
          localVarRequestBuilder.build(),
          HttpResponse.BodyHandlers.ofInputStream());
      if (memberVarResponseInterceptor != null) {
        memberVarResponseInterceptor.accept(localVarResponse);
      }
      if (isErrorResponse(localVarResponse)) {
        throw new ApiException(localVarResponse.statusCode(),
            "getLogs call received non-success response",
            localVarResponse.headers(),
            localVarResponse.body() == null ? null : new String(localVarResponse.body().readAllBytes()));
      }

      final File tmpFile = File.createTempFile("patched-logs-api", "response"); // CHANGED
      tmpFile.deleteOnExit(); // CHANGED

      FileUtils.copyInputStreamToFile(localVarResponse.body(), tmpFile); // CHANGED

      return new ApiResponse<File>(
          localVarResponse.statusCode(),
          localVarResponse.headers().map(),
          tmpFile // CHANGED
      );
    } catch (final IOException e) {
      throw new ApiException(e);
    } catch (final InterruptedException e) {
      Thread.currentThread().interrupt();
      throw new ApiException(e);
    }
  }

  private Boolean isErrorResponse(final HttpResponse<InputStream> httpResponse) {
    return httpResponse.statusCode() / 100 != 2;
  }

  private HttpRequest.Builder getLogsRequestBuilder(final LogsRequestBody logsRequestBody) throws ApiException {
    // verify the required parameter 'logsRequestBody' is set
    if (logsRequestBody == null) {
      throw new ApiException(400, "Missing the required parameter 'logsRequestBody' when calling getLogs");
    }

    final HttpRequest.Builder localVarRequestBuilder = HttpRequest.newBuilder();

    final String localVarPath = "/v1/logs/get";

    localVarRequestBuilder.uri(URI.create(memberVarBaseUri + localVarPath));

    localVarRequestBuilder.header("Content-Type", "application/json");

    localVarRequestBuilder.header("Accept", "text/plain"); // CHANGED

    try {
      final byte[] localVarPostBody = memberVarObjectMapper.writeValueAsBytes(logsRequestBody);
      localVarRequestBuilder.method("POST", HttpRequest.BodyPublishers.ofByteArray(localVarPostBody));
    } catch (final IOException e) {
      throw new ApiException(e);
    }
    if (memberVarReadTimeout != null) {
      localVarRequestBuilder.timeout(memberVarReadTimeout);
    }
    if (memberVarInterceptor != null) {
      memberVarInterceptor.accept(localVarRequestBuilder);
    }
    return localVarRequestBuilder;
  }

}
