/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.ADMIN;
import static io.airbyte.commons.auth.AuthRoleConstants.EDITOR;

import io.airbyte.api.generated.DestinationOauthApi;
import io.airbyte.api.model.generated.CompleteDestinationOAuthRequest;
import io.airbyte.api.model.generated.DestinationOauthConsentRequest;
import io.airbyte.api.model.generated.OAuthConsentRead;
import io.airbyte.api.model.generated.SetInstancewideDestinationOauthParamsRequestBody;
import io.airbyte.commons.server.handlers.OAuthHandler;
import io.micronaut.context.annotation.Context;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;
import java.util.Map;

@Controller("/api/v1/destination_oauths")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Context
@Secured(SecurityRule.IS_AUTHENTICATED)
public class DestinationOauthApiController implements DestinationOauthApi {

  private final OAuthHandler oAuthHandler;

  public DestinationOauthApiController(final OAuthHandler oAuthHandler) {
    this.oAuthHandler = oAuthHandler;
  }

  @Post("/complete_oauth")
  @Secured({EDITOR})
  @Override
  public Map<String, Object> completeDestinationOAuth(final CompleteDestinationOAuthRequest completeDestinationOAuthRequest) {
    return ApiHelper.execute(() -> oAuthHandler.completeDestinationOAuth(completeDestinationOAuthRequest));
  }

  @Post("/get_consent_url")
  @Secured({EDITOR})
  @Override
  public OAuthConsentRead getDestinationOAuthConsent(final DestinationOauthConsentRequest destinationOauthConsentRequest) {
    return ApiHelper.execute(() -> oAuthHandler.getDestinationOAuthConsent(destinationOauthConsentRequest));
  }

  @Post("/oauth_params/create")
  @Secured({ADMIN})
  @Override
  public void setInstancewideDestinationOauthParams(final SetInstancewideDestinationOauthParamsRequestBody setInstancewideDestinationOauthParamsRequestBody) {
    ApiHelper.execute(() -> {
      oAuthHandler.setDestinationInstancewideOauthParams(setInstancewideDestinationOauthParamsRequestBody);
      return null;
    });
  }

}
