/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.server.forwardingClient;

import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.micronaut.http.HttpResponse;
import java.util.UUID;
import javax.validation.constraints.NotBlank;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class InternalApiWrapper {

  public static final String GATEWAY_AUTH_HEADER = "X-Endpoint-API-UserInfo";

  private final ConfigApiClient client;

  public InternalApiWrapper(final ConfigApiClient client) {
    this.client = client;
  }

  public HttpResponse<String> sync(@NotBlank final UUID connectionId, final String authorization) {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(connectionId);
    final HttpResponse<String> res = client.sync(connectionIdRequestBody, authorization);
    log.debug("HttpResponse body: " + res.body());
    return res;
  }

  public HttpResponse<String> reset(@NotBlank final UUID connectionId) {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(connectionId);
    final HttpResponse<String> res = client.reset(connectionIdRequestBody);
    log.debug("HttpResponse body: " + res.body());
    return res;
  }

}
