/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import com.google.common.collect.ImmutableMap;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.flows.AsanaOAuthFlow;
import io.airbyte.oauth.flows.GithubOAuthFlow;
import io.airbyte.oauth.flows.HarvestOAuthFlow;
import io.airbyte.oauth.flows.HubspotOAuthFlow;
import io.airbyte.oauth.flows.IntercomOAuthFlow;
import io.airbyte.oauth.flows.LinkedinAdsOAuthFlow;
import io.airbyte.oauth.flows.PipeDriveOAuthFlow;
import io.airbyte.oauth.flows.QuickbooksOAuthFlow;
import io.airbyte.oauth.flows.SalesforceOAuthFlow;
import io.airbyte.oauth.flows.SlackOAuthFlow;
import io.airbyte.oauth.flows.SnapchatMarketingOAuthFlow;
import io.airbyte.oauth.flows.SurveymonkeyOAuthFlow;
import io.airbyte.oauth.flows.TrelloOAuthFlow;
import io.airbyte.oauth.flows.facebook.FacebookMarketingOAuthFlow;
import io.airbyte.oauth.flows.facebook.FacebookPagesOAuthFlow;
import io.airbyte.oauth.flows.facebook.InstagramOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleAdsOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleAnalyticsOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleSearchConsoleOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleSheetsOAuthFlow;
import io.airbyte.oauth.flows.google.YouTubeAnalyticsOAuthFlow;
import java.net.http.HttpClient;
import java.util.Map;

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
        .put("airbyte/source-harvest", new HarvestOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-hubspot", new HubspotOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-intercom", new IntercomOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-instagram", new InstagramOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-pipedrive", new PipeDriveOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-quickbooks", new QuickbooksOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-linkedin-ads", new LinkedinAdsOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-salesforce", new SalesforceOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-slack", new SlackOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-snapchat-marketing", new SnapchatMarketingOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-surveymonkey", new SurveymonkeyOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-trello", new TrelloOAuthFlow(configRepository, httpClient))
        .put("airbyte/source-youtube-analytics", new YouTubeAnalyticsOAuthFlow(configRepository, httpClient))
        .build();
  }

  public OAuthFlowImplementation create(final StandardSourceDefinition sourceDefinition) {
    return create(sourceDefinition.getDockerRepository());
  }

  public OAuthFlowImplementation create(final StandardDestinationDefinition destinationDefinition) {
    return create(destinationDefinition.getDockerRepository());
  }

  private OAuthFlowImplementation create(final String imageName) {
    if (OAUTH_FLOW_MAPPING.containsKey(imageName)) {
      return OAUTH_FLOW_MAPPING.get(imageName);
    } else {
      throw new IllegalStateException(
          String.format("Requested OAuth implementation for %s, but it is not included in the oauth mapping.", imageName));
    }
  }

}
