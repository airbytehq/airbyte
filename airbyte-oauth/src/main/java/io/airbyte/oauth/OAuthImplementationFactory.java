/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.flows.*;
import io.airbyte.oauth.flows.facebook.FacebookMarketingOAuthFlow;
import io.airbyte.oauth.flows.facebook.FacebookPagesOAuthFlow;
import io.airbyte.oauth.flows.facebook.InstagramOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleAdsOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleAnalyticsOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleSearchConsoleOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleSheetsOAuthFlow;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.UUID;

public class OAuthImplementationFactory {

  private final Map<String, OAuthFlowImplementation> OAUTH_FLOW_MAPPING;

  public OAuthImplementationFactory(final ConfigRepository configRepository, final HttpClient httpClient) {
    OAUTH_FLOW_MAPPING = ImmutableMap.<String, OAuthFlowImplementation>builder()
        .put("airbyte/source-asana", new AsanaOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-facebook-marketing", new FacebookMarketingOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-facebook-pages", new FacebookPagesOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-github", new GithubOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-google-ads", new GoogleAdsOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-google-analytics-v4", new GoogleAnalyticsOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-google-search-console", new GoogleSearchConsoleOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-google-sheets", new GoogleSheetsOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-instagram", new InstagramOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-salesforce", new SalesforceOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-slack", new SlackOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-surveymonkey", new SurveymonkeyOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-trello", new TrelloOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-hubspot", new HubspotOAuthFlow(configRepository, httpClient))
        .build();
  }

  public OAuthFlowImplementation create(final String imageName, final UUID workspaceId) {
    if (OAUTH_FLOW_MAPPING.containsKey(imageName)) {
      return OAUTH_FLOW_MAPPING.get(imageName);
    } else {
      throw new IllegalStateException(
          String.format("Requested OAuth implementation for %s, but it is not included in the oauth mapping.", imageName));
    }
  }

}
