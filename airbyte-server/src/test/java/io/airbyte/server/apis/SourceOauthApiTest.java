/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.generated.OAuthConsentRead;
import io.airbyte.api.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.env.Environment;
import io.micronaut.core.util.StringUtils;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpStatus;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import java.io.IOException;
import java.util.HashMap;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@MicronautTest
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.TRUE,
          value = StringUtils.TRUE)
@Requires(env = {Environment.TEST})
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class SourceOauthApiTest extends BaseControllerTest {

  @Test
  void testCompleteSourceOAuth() throws IOException, JsonValidationException, ConfigNotFoundException {
    Mockito.when(oAuthHandler.completeSourceOAuth(Mockito.any()))
        .thenReturn(new HashMap<>())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/source_oauths/complete_oauth";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGetSourceOAuthConsent() throws IOException, JsonValidationException, ConfigNotFoundException {
    Mockito.when(oAuthHandler.getSourceOAuthConsent(Mockito.any()))
        .thenReturn(new OAuthConsentRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/source_oauths/get_consent_url";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testSetInstancewideSourceOauthParams() throws IOException, JsonValidationException {
    Mockito.doNothing()
        .when(oAuthHandler).setSourceInstancewideOauthParams(Mockito.any());

    final String path = "/api/v1/source_oauths/oauth_params/create";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
  }

}
