/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.flows.AsanaOAuthFlow;
import io.airbyte.oauth.flows.GithubOAuthFlow;
import io.airbyte.oauth.flows.SalesforceOAuthFlow;
import io.airbyte.oauth.flows.TrelloOAuthFlow;
import io.airbyte.oauth.flows.facebook.FacebookMarketingOAuthFlow;
import io.airbyte.oauth.flows.facebook.FacebookPagesOAuthFlow;
import io.airbyte.oauth.flows.facebook.InstagramOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleAdsOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleAnalyticsOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleSearchConsoleOAuthFlow;
import io.airbyte.oauth.flows.google.GoogleSheetsOAuthFlow;
import java.util.Map;
import java.util.UUID;

public class OAuthImplementationFactory {

  private final Map<String, OAuthFlowImplementation> OAUTH_FLOW_MAPPING;

  public OAuthImplementationFactory(final ConfigRepository configRepository) {
    OAUTH_FLOW_MAPPING = ImmutableMap.<String, OAuthFlowImplementation>builder()
        .put("airbyte/source-asana", new AsanaOAuthFlow(configRepository))
        .put("airbyte/source-facebook-marketing", new FacebookMarketingOAuthFlow(configRepository))
        .put("airbyte/source-facebook-pages", new FacebookPagesOAuthFlow(configRepository))
        .put("airbyte/source-github", new GithubOAuthFlow(configRepository))
        .put("airbyte/source-google-ads", new GoogleAdsOAuthFlow(configRepository))
        .put("airbyte/source-google-analytics-v4", new GoogleAnalyticsOAuthFlow(configRepository))
        .put("airbyte/source-google-search-console", new GoogleSearchConsoleOAuthFlow(configRepository))
        .put("airbyte/source-google-sheets", new GoogleSheetsOAuthFlow(configRepository))
        .put("airbyte/source-instagram", new InstagramOAuthFlow(configRepository))
        .put("airbyte/source-salesforce", new SalesforceOAuthFlow(configRepository))
        .put("airbyte/source-trello", new TrelloOAuthFlow(configRepository))
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
