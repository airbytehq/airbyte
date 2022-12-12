/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.SourceOauthApi;
import io.airbyte.api.model.generated.CompleteSourceOauthRequest;
import io.airbyte.api.model.generated.OAuthConsentRead;
import io.airbyte.api.model.generated.SetInstancewideSourceOauthParamsRequestBody;
import io.airbyte.api.model.generated.SourceOauthConsentRequest;
import io.airbyte.server.handlers.OAuthHandler;
import io.micronaut.http.annotation.Body;
import java.util.Map;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/source_oauths")
@AllArgsConstructor
public class SourceOauthApiController implements SourceOauthApi {

  private final OAuthHandler oAuthHandler;

  @Override
  public Map<String, Object> completeSourceOAuth(@Body final CompleteSourceOauthRequest completeSourceOauthRequest) {
    return ApiHelper.execute(() -> oAuthHandler.completeSourceOAuth(completeSourceOauthRequest));
  }

  @Override
  public OAuthConsentRead getSourceOAuthConsent(@Body final SourceOauthConsentRequest sourceOauthConsentRequest) {
    return ApiHelper.execute(() -> oAuthHandler.getSourceOAuthConsent(sourceOauthConsentRequest));
  }

  @Override
  public void setInstancewideSourceOauthParams(@Body final SetInstancewideSourceOauthParamsRequestBody setInstancewideSourceOauthParamsRequestBody) {
    ApiHelper.execute(() -> {
      oAuthHandler.setSourceInstancewideOauthParams(setInstancewideSourceOauthParamsRequestBody);
      return null;
    });
  }

}
