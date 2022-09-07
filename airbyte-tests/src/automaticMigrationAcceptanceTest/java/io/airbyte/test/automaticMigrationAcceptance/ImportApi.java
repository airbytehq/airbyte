/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.automaticMigrationAcceptance;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.invoker.generated.ApiResponse;
import io.airbyte.api.client.model.generated.ImportRead;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpRequest.Builder;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.function.Consumer;

/**
 * The reason we are using this class instead of
 * {@link io.airbyte.api.client.generated.DeploymentApi is cause there is a bug in the the method
 * {@link io.airbyte.api.client.generated.DeploymentApi#importArchiveRequestBuilder(File)}, The
 * method specifies the content type as `localVarRequestBuilder.header("Content-Type",
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

  public ImportApi(final ApiClient apiClient) {
    memberVarHttpClient = apiClient.getHttpClient();
    memberVarObjectMapper = apiClient.getObjectMapper();
    memberVarBaseUri = apiClient.getBaseUri();
    memberVarInterceptor = apiClient.getRequestInterceptor();
    memberVarReadTimeout = apiClient.getReadTimeout();
    memberVarResponseInterceptor = apiClient.getResponseInterceptor();
  }

  public ImportRead importArchive(final File body) throws ApiException {
    final ApiResponse<ImportRead> localVarResponse = importArchiveWithHttpInfo(body);
    return localVarResponse.getData();
  }

  public ApiResponse<ImportRead> importArchiveWithHttpInfo(final File body) throws ApiException {
    final HttpRequest.Builder localVarRequestBuilder = importArchiveRequestBuilder(body);
    try {
      final HttpResponse<InputStream> localVarResponse = memberVarHttpClient.send(
          localVarRequestBuilder.build(),
          HttpResponse.BodyHandlers.ofInputStream());
      if (memberVarResponseInterceptor != null) {
        memberVarResponseInterceptor.accept(localVarResponse);
      }
      if (errorResponse(localVarResponse)) {
        throw new ApiException(localVarResponse.statusCode(),
            "importArchive call received non-success response",
            localVarResponse.headers(),
            localVarResponse.body() == null ? null
                : new String(localVarResponse.body().readAllBytes(), StandardCharsets.UTF_8));
      }
      return new ApiResponse<ImportRead>(
          localVarResponse.statusCode(),
          localVarResponse.headers().map(),
          memberVarObjectMapper.readValue(localVarResponse.body(), new TypeReference<ImportRead>() {}));
    } catch (final IOException e) {
      throw new ApiException(e);
    } catch (final InterruptedException e) {
      Thread.currentThread().interrupt();
      throw new ApiException(e);
    }
  }

  private Boolean errorResponse(final HttpResponse<InputStream> localVarResponse) {
    return localVarResponse.statusCode() / 100 != 2;
  }

  private HttpRequest.Builder importArchiveRequestBuilder(final File body) throws ApiException {
    // verify the required parameter 'body' is set
    if (body == null) {
      throw new ApiException(400,
          "Missing the required parameter 'body' when calling importArchive");
    }

    final HttpRequest.Builder localVarRequestBuilder = HttpRequest.newBuilder();

    final String localVarPath = "/v1/deployment/import";

    localVarRequestBuilder.uri(URI.create(memberVarBaseUri + localVarPath));

    localVarRequestBuilder.header("Content-Type", "application/x-gzip");
    localVarRequestBuilder.header("Accept", "application/json");

    try {
      localVarRequestBuilder.method("POST", HttpRequest.BodyPublishers.ofFile(body.toPath()));
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
