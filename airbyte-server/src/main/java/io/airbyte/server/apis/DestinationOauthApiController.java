/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.DestinationOauthApi;
import io.airbyte.api.model.generated.CompleteDestinationOAuthRequest;
import io.airbyte.api.model.generated.DestinationOauthConsentRequest;
import io.airbyte.api.model.generated.OAuthConsentRead;
import io.airbyte.api.model.generated.SetInstancewideDestinationOauthParamsRequestBody;
import io.airbyte.server.handlers.OAuthHandler;
import io.micronaut.context.annotation.Context;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import java.util.Map;

@Controller("/api/v1/destination_oauths")
@Context
public class DestinationOauthApiController implements DestinationOauthApi {

  private final OAuthHandler oAuthHandler;

  public DestinationOauthApiController(final OAuthHandler oAuthHandler) {
    this.oAuthHandler = oAuthHandler;
  }

  @Post("/complete_oauth")
  @Override
  public Map<String, Object> completeDestinationOAuth(final CompleteDestinationOAuthRequest completeDestinationOAuthRequest) {
    return ApiHelper.execute(() -> oAuthHandler.completeDestinationOAuth(completeDestinationOAuthRequest));
  }

  @Post("/get_consent_url")
  @Override
  public OAuthConsentRead getDestinationOAuthConsent(final DestinationOauthConsentRequest destinationOauthConsentRequest) {
    return ApiHelper.execute(() -> oAuthHandler.getDestinationOAuthConsent(destinationOauthConsentRequest));
  }

  @Post("/oauth_params/create")
  @Override
  public void setInstancewideDestinationOauthParams(final SetInstancewideDestinationOauthParamsRequestBody setInstancewideDestinationOauthParamsRequestBody) {
    ApiHelper.execute(() -> {
      oAuthHandler.setDestinationInstancewideOauthParams(setInstancewideDestinationOauthParamsRequestBody);
      return null;
    });
  }

}
