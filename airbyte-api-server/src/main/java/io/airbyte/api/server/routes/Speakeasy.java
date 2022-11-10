/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.server.routes;


import com.fasterxml.jackson.databind.ObjectMapper;
import dev.speakeasyapi.micronaut.EnableSpeakeasy;
import dev.speakeasyapi.sdk.SpeakeasyMiddlewareController;
import dev.speakeasyapi.sdk.models.SpeakeasyAccessTokenFilterBuilder;
import dev.speakeasyapi.sdk.models.SpeakeasyAccessTokenFilterOperator;
import io.airbyte.api.server.models.AirbyteAccessToken;
import io.micronaut.context.annotation.Value;
import io.micronaut.http.annotation.RequestAttribute;
import java.io.IOException;
import java.net.URI;
import java.time.Instant;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import javax.ws.rs.GET;
import javax.ws.rs.HeaderParam;
import javax.ws.rs.Path;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Response;

@Path("/speakeasy_portal_login_token")
@EnableSpeakeasy
public class Speakeasy {
  @Value("${airbyte.speakeasy.callback-url}")
  String callbackUrlValue;

  @GET
  public Response getPortalLoginAccessToken(
      @HeaderParam("Authorization") String accessToken,
      @QueryParam("callbackUrl") Optional<String> callbackUrl,
      @RequestAttribute(SpeakeasyMiddlewareController.Key) SpeakeasyMiddlewareController controller
  ) {
    try {
      AirbyteAccessToken airbyteAccessToken = getAirbyteAccessTokenFromBearerToken(
          accessToken
      );
      String redirectUrl = callbackUrl.orElse(callbackUrlValue);

      Map<String, String> claims = new HashMap<>();
      claims.put(AirbyteAccessToken.SUBJECT, airbyteAccessToken.getSubject());
      claims.put(AirbyteAccessToken.USER_ID, airbyteAccessToken.getSubject());
      claims.put(AirbyteAccessToken.EMAIL, airbyteAccessToken.getEmail());
      claims.put(AirbyteAccessToken.EMAIL_VERIFIED, airbyteAccessToken.getEmailVerified());

      // Populate with any permissions you want enabled/disabled for the user
      Map<String, Boolean> permissions = new HashMap<>();
      permissions.put("end_user:api_keys:read", true);
      permissions.put("end_user:api_keys:write", true);

      return Response
          .status(307)
          .location(
              URI.create(redirectUrl
                  + "?speakeasyAccessToken="
                  + controller.getPortalLoginToken(
                  airbyteAccessToken.getSubject(),
                  airbyteAccessToken.getEmail(),
                  claims,
                  permissions,
                  new SpeakeasyAccessTokenFilterBuilder()
                      .withTimeFilter(
                          Instant.now().minusSeconds(60*60*24),
                          SpeakeasyAccessTokenFilterOperator.GreaterThan
                      )
                      .build()
              ))
          )
          .build();
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private static AirbyteAccessToken getAirbyteAccessTokenFromBearerToken(String accessToken) throws IOException {

    if (accessToken.length() < 7) {
      return null;
    }
    // Skip Bearer
    var token = accessToken.substring(7);

    // Middle part is our payload
    var object = token.split("\\.");
    if (object.length < 3) {
      return null;
    }

    var jsonString = Base64.getDecoder().decode(object[1]);
    return new ObjectMapper().readValue(jsonString, AirbyteAccessToken.class);
  }
}
