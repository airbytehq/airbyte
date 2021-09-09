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

package io.airbyte.server.handlers;

import io.airbyte.api.model.CompleteDestinationOAuthRequest;
import io.airbyte.api.model.CompleteSourceOauthRequest;
import io.airbyte.api.model.DestinationOauthConsentRequest;
import io.airbyte.api.model.OAuthConsentRead;
import io.airbyte.api.model.SetInstancewideDestinationOauthParamsRequestBody;
import io.airbyte.api.model.SetInstancewideSourceOauthParamsRequestBody;
import io.airbyte.api.model.SourceOauthConsentRequest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.OAuthFlowImplementation;
import io.airbyte.oauth.OAuthImplementationFactory;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Map;
import java.util.UUID;

public class OAuthHandler {

  private final ConfigRepository configRepository;
  private final OAuthImplementationFactory oAuthImplementationFactory;

  public OAuthHandler(ConfigRepository configRepository) {
    this.configRepository = configRepository;
    this.oAuthImplementationFactory = new OAuthImplementationFactory(configRepository);
  }

  public OAuthConsentRead getSourceOAuthConsent(SourceOauthConsentRequest sourceDefinitionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final OAuthFlowImplementation oAuthFlowImplementation = getSourceOAuthFlowImplementation(sourceDefinitionIdRequestBody.getSourceDefinitionId());
    return new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getSourceConsentUrl(
        sourceDefinitionIdRequestBody.getWorkspaceId(),
        sourceDefinitionIdRequestBody.getSourceDefinitionId(),
        sourceDefinitionIdRequestBody.getRedirectUrl()));
  }

  public OAuthConsentRead getDestinationOAuthConsent(DestinationOauthConsentRequest destinationDefinitionIdRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final OAuthFlowImplementation oAuthFlowImplementation =
        getDestinationOAuthFlowImplementation(destinationDefinitionIdRequestBody.getDestinationDefinitionId());
    return new OAuthConsentRead().consentUrl(oAuthFlowImplementation.getDestinationConsentUrl(
        destinationDefinitionIdRequestBody.getWorkspaceId(),
        destinationDefinitionIdRequestBody.getDestinationDefinitionId(),
        destinationDefinitionIdRequestBody.getRedirectUrl()));
  }

  public Map<String, Object> completeSourceOAuth(CompleteSourceOauthRequest oauthSourceRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final OAuthFlowImplementation oAuthFlowImplementation = getSourceOAuthFlowImplementation(oauthSourceRequestBody.getSourceDefinitionId());
    return oAuthFlowImplementation.completeSourceOAuth(
        oauthSourceRequestBody.getWorkspaceId(),
        oauthSourceRequestBody.getSourceDefinitionId(),
        oauthSourceRequestBody.getQueryParams(),
        oauthSourceRequestBody.getRedirectUrl());
  }

  public Map<String, Object> completeDestinationOAuth(CompleteDestinationOAuthRequest oauthDestinationRequestBody)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final OAuthFlowImplementation oAuthFlowImplementation =
        getDestinationOAuthFlowImplementation(oauthDestinationRequestBody.getDestinationDefinitionId());
    return oAuthFlowImplementation.completeDestinationOAuth(
        oauthDestinationRequestBody.getWorkspaceId(),
        oauthDestinationRequestBody.getDestinationDefinitionId(),
        oauthDestinationRequestBody.getQueryParams(),
        oauthDestinationRequestBody.getRedirectUrl());
  }

  public void setDestinationInstancewideOauthParams(SetInstancewideDestinationOauthParamsRequestBody requestBody)
      throws JsonValidationException, IOException {
    DestinationOAuthParameter param = new DestinationOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withConfiguration(Jsons.jsonNode(requestBody.getParams()))
        .withDestinationDefinitionId(requestBody.getDestinationDefinitionId());
    configRepository.writeDestinationOAuthParam(param);
  }

  public void setSourceInstancewideOauthParams(SetInstancewideSourceOauthParamsRequestBody requestBody) throws JsonValidationException, IOException {
    SourceOAuthParameter param = new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withConfiguration(Jsons.jsonNode(requestBody.getParams()))
        .withSourceDefinitionId(requestBody.getSourceDefinitionId());
    configRepository.writeSourceOAuthParam(param);
  }

  private OAuthFlowImplementation getSourceOAuthFlowImplementation(UUID sourceDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSourceDefinition standardSourceDefinition = configRepository
        .getStandardSourceDefinition(sourceDefinitionId);
    return oAuthImplementationFactory.create(standardSourceDefinition.getDockerRepository());
  }

  private OAuthFlowImplementation getDestinationOAuthFlowImplementation(UUID destinationDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardDestinationDefinition standardDestinationDefinition = configRepository
        .getStandardDestinationDefinition(destinationDefinitionId);
    return oAuthImplementationFactory.create(standardDestinationDefinition.getDockerRepository());
  }

}
