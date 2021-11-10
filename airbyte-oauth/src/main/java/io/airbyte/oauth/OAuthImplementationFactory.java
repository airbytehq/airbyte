/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import com.google.common.collect.ImmutableMap;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.flows.*;
import io.airbyte.oauth.flows.facebook.FacebookMarketingOAuthFlow;
import io.airbyte.oauth.flows.facebook.FacebookPagesOAuthFlow;
import io.airbyte.oauth.flows.facebook.InstagramOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleAdsOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleAnalyticsOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleSearchConsoleOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleSheetsOAuthFlow;
import java.lang.reflect.InvocationTargetException;
import java.net.http.HttpClient;
import java.util.Map;

public class OAuthImplementationFactory {

  private static final Map<String, Class<? extends OAuthFlowImplementation>> OAUTH_FLOW_MAPPING =
      ImmutableMap.<String, Class<? extends OAuthFlowImplementation>>builder()
          .put("airbyte/source-asana", AsanaOAuthFlow.class)
          .put("airbyte/source-facebook-marketing", FacebookMarketingOAuthFlow.class)
          .put("airbyte/source-facebook-pages", FacebookPagesOAuthFlow.class)
          .put("airbyte/source-github", GithubOAuthFlow.class)
          .put("airbyte/source-google-ads", GoogleAdsOAuthFlow.class)
          .put("airbyte/source-google-analytics-v4", GoogleAnalyticsOAuthFlow.class)
          .put("airbyte/source-google-search-console", GoogleSearchConsoleOAuthFlow.class)
          .put("airbyte/source-google-sheets", GoogleSheetsOAuthFlow.class)
          .put("airbyte/source-hubspot", HubspotOAuthFlow.class)
          .put("airbyte/source-intercom", IntercomOAuthFlow.class)
          .put("airbyte/source-instagram", InstagramOAuthFlow.class)
          .put("airbyte/source-salesforce", SalesforceOAuthFlow.class)
          .put("airbyte/source-slack", SlackOAuthFlow.class)
          .put("airbyte/source-surveymonkey", SurveymonkeyOAuthFlow.class)
          .put("airbyte/source-trello", TrelloOAuthFlow.class)
          .put("airbyte/source-quickbooks", QuickbooksOAuthFlow.class)
          .build();
  private final ConfigRepository configRepository;
  private final HttpClient httpClient;

  public OAuthImplementationFactory(final ConfigRepository configRepository, final HttpClient httpClient) {
    this.configRepository = configRepository;
    this.httpClient = httpClient;
  }

  public OAuthFlowImplementation create(final StandardSourceDefinition sourceDefinition) {
    return create(sourceDefinition.getDockerRepository());
  }

  public OAuthFlowImplementation create(final StandardDestinationDefinition destinationDefinition) {
    return create(destinationDefinition.getDockerRepository());
  }


  private OAuthFlowImplementation create(final String imageName) {
    if (OAUTH_FLOW_MAPPING.containsKey(imageName)) {
      try {
        var implementation = OAUTH_FLOW_MAPPING.get(imageName).getDeclaredConstructor(ConfigRepository.class, HttpClient.class);
        return implementation.newInstance(configRepository, httpClient);
      } catch (InvocationTargetException | InstantiationException | IllegalAccessException | NoSuchMethodException e) {
        throw new IllegalStateException(
            String.format("Requested OAuth implementation for %s, but it could not be instantiated.", imageName), e);
      }
    } else {
      throw new IllegalStateException(
          String.format("Requested OAuth implementation for %s, but it is not included in the oauth mapping.", imageName));
    }
  }

}
