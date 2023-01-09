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
import java.util.Map;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/destination_oauths")
@AllArgsConstructor
public class DestinationOauthApiController implements DestinationOauthApi {

  private final OAuthHandler oAuthHandler;

  @Override
  public Map<String, Object> completeDestinationOAuth(final CompleteDestinationOAuthRequest completeDestinationOAuthRequest) {
    return ApiHelper.execute(() -> oAuthHandler.completeDestinationOAuth(completeDestinationOAuthRequest));
  }

  @Override
  public OAuthConsentRead getDestinationOAuthConsent(final DestinationOauthConsentRequest destinationOauthConsentRequest) {
    return ApiHelper.execute(() -> oAuthHandler.getDestinationOAuthConsent(destinationOauthConsentRequest));
  }

  @Override
  public void setInstancewideDestinationOauthParams(final SetInstancewideDestinationOauthParamsRequestBody setInstancewideDestinationOauthParamsRequestBody) {
    ApiHelper.execute(() -> {
      oAuthHandler.setDestinationInstancewideOauthParams(setInstancewideDestinationOauthParamsRequestBody);
      return null;
    });
  }

}
