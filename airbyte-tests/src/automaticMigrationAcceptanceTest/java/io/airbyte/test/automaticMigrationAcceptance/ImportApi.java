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

package io.airbyte.test.automaticMigrationAcceptance;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.invoker.ApiResponse;
import io.airbyte.api.client.model.ImportRead;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpRequest.Builder;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.function.Consumer;

/**
 * The reason we are using this class instead of {@link io.airbyte.api.client.DeploymentApi is cause
 * there is a bug in the the method
 * {@link io.airbyte.api.client.DeploymentApi#importArchiveRequestBuilder(File)}, The method
 * specifies the content type as `localVarRequestBuilder.header("Content-Type",
 * "application/json");` but its supposed to be localVarRequestBuilder.header("Content-Type",
 * "application/x-gzip");
 */
public class ImportApi {

  private final HttpClient memberVarHttpClient;
  private final ObjectMapper memberVarObjectMapper;
  private final String memberVarBaseUri;
  private final Consumer<Builder> memberVarInterceptor;
  private final Duration memberVarReadTimeout;
  private final Consumer<HttpResponse<InputStream>> memberVarResponseInterceptor;

  public ImportApi(ApiClient apiClient) {
    memberVarHttpClient = apiClient.getHttpClient();
    memberVarObjectMapper = apiClient.getObjectMapper();
    memberVarBaseUri = apiClient.getBaseUri();
    memberVarInterceptor = apiClient.getRequestInterceptor();
    memberVarReadTimeout = apiClient.getReadTimeout();
    memberVarResponseInterceptor = apiClient.getResponseInterceptor();
  }

  public ImportRead importArchive(File body) throws ApiException {
    ApiResponse<ImportRead> localVarResponse = importArchiveWithHttpInfo(body);
    return localVarResponse.getData();
  }

  public ApiResponse<ImportRead> importArchiveWithHttpInfo(File body) throws ApiException {
    HttpRequest.Builder localVarRequestBuilder = importArchiveRequestBuilder(body);
    try {
      HttpResponse<InputStream> localVarResponse = memberVarHttpClient.send(
          localVarRequestBuilder.build(),
          HttpResponse.BodyHandlers.ofInputStream());
      if (memberVarResponseInterceptor != null) {
        memberVarResponseInterceptor.accept(localVarResponse);
      }
      if (localVarResponse.statusCode() / 100 != 2) {
        throw new ApiException(localVarResponse.statusCode(),
            "importArchive call received non-success response",
            localVarResponse.headers(),
            localVarResponse.body() == null ? null
                : new String(localVarResponse.body().readAllBytes()));
      }
      return new ApiResponse<ImportRead>(
          localVarResponse.statusCode(),
          localVarResponse.headers().map(),
          memberVarObjectMapper.readValue(localVarResponse.body(), new TypeReference<ImportRead>() {}));
    } catch (IOException e) {
      throw new ApiException(e);
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
      throw new ApiException(e);
    }
  }

  private HttpRequest.Builder importArchiveRequestBuilder(File body) throws ApiException {
    // verify the required parameter 'body' is set
    if (body == null) {
      throw new ApiException(400,
          "Missing the required parameter 'body' when calling importArchive");
    }

    HttpRequest.Builder localVarRequestBuilder = HttpRequest.newBuilder();

    String localVarPath = "/v1/deployment/import";

    localVarRequestBuilder.uri(URI.create(memberVarBaseUri + localVarPath));

    localVarRequestBuilder.header("Content-Type", "application/x-gzip");
    localVarRequestBuilder.header("Accept", "application/json");

    try {
      localVarRequestBuilder.method("POST", HttpRequest.BodyPublishers.ofFile(body.toPath()));
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
