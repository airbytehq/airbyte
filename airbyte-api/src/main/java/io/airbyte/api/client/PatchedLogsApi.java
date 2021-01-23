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

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.invoker.ApiResponse;
import io.airbyte.api.client.model.LogsRequestBody;
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
 * This class is a copy of {@link LogsApi} except it allows Accept: text/plain. Without this
 * modification, {@link LogsApi} returns a 406 because the generated code requests the wrong
 * response type.
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

  public PatchedLogsApi(ApiClient apiClient) {
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
  public File getLogs(LogsRequestBody logsRequestBody) throws ApiException {
    ApiResponse<File> localVarResponse = getLogsWithHttpInfo(logsRequestBody);
    return localVarResponse.getData();
  }

  /**
   * Get logs
   *
   * @param logsRequestBody (required)
   * @return ApiResponse&lt;File&gt;
   * @throws ApiException if fails to make API call
   */
  public ApiResponse<File> getLogsWithHttpInfo(LogsRequestBody logsRequestBody) throws ApiException {
    HttpRequest.Builder localVarRequestBuilder = getLogsRequestBuilder(logsRequestBody);
    try {
      HttpResponse<InputStream> localVarResponse = memberVarHttpClient.send(
          localVarRequestBuilder.build(),
          HttpResponse.BodyHandlers.ofInputStream());
      if (memberVarResponseInterceptor != null) {
        memberVarResponseInterceptor.accept(localVarResponse);
      }
      if (localVarResponse.statusCode() / 100 != 2) {
        throw new ApiException(localVarResponse.statusCode(),
            "getLogs call received non-success response",
            localVarResponse.headers(),
            localVarResponse.body() == null ? null : new String(localVarResponse.body().readAllBytes()));
      }

      File tmpFile = File.createTempFile("patched-logs-api", "response"); // CHANGED
      tmpFile.deleteOnExit(); // CHANGED

      FileUtils.copyInputStreamToFile(localVarResponse.body(), tmpFile); // CHANGED

      return new ApiResponse<File>(
          localVarResponse.statusCode(),
          localVarResponse.headers().map(),
          tmpFile // CHANGED
      );
    } catch (IOException e) {
      throw new ApiException(e);
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
      throw new ApiException(e);
    }
  }

  private HttpRequest.Builder getLogsRequestBuilder(LogsRequestBody logsRequestBody) throws ApiException {
    // verify the required parameter 'logsRequestBody' is set
    if (logsRequestBody == null) {
      throw new ApiException(400, "Missing the required parameter 'logsRequestBody' when calling getLogs");
    }

    HttpRequest.Builder localVarRequestBuilder = HttpRequest.newBuilder();

    String localVarPath = "/v1/logs/get";

    localVarRequestBuilder.uri(URI.create(memberVarBaseUri + localVarPath));

    localVarRequestBuilder.header("Content-Type", "application/json");

    localVarRequestBuilder.header("Accept", "text/plain"); // CHANGED

    try {
      byte[] localVarPostBody = memberVarObjectMapper.writeValueAsBytes(logsRequestBody);
      localVarRequestBuilder.method("POST", HttpRequest.BodyPublishers.ofByteArray(localVarPostBody));
    } catch (IOException e) {
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
