/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import com.google.common.collect.ImmutableMap;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.flows.*;
import io.airbyte.oauth.flows.facebook.*;
import io.airbyte.oauth.flows.google.*;
import java.net.http.HttpClient;
import java.util.Map;

public class OAuthImplementationFactory {

  private final Map<String, OAuthFlowImplementation> OAUTH_FLOW_MAPPING;

  public OAuthImplementationFactory(final ConfigRepository configRepository, final HttpClient httpClient) {
    OAUTH_FLOW_MAPPING = ImmutableMap.<String, OAuthFlowImplementation>builder()
        .put("yuanrui2014/source-amazon-ads", new AmazonAdsOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-amazon-seller-partner", new AmazonSellerPartnerOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-asana", new AsanaOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-ebay", new EbayOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-facebook-marketing", new FacebookMarketingOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-facebook-pages", new FacebookPagesOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-github", new GithubOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-google-ads", new GoogleAdsOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-google-analytics-v4", new GoogleAnalyticsViewIdOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-google-analytics-data-api", new GoogleAnalyticsPropertyIdOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-google-search-console", new GoogleSearchConsoleOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-google-sheets", new GoogleSheetsOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-harvest", new HarvestOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-hubspot", new HubspotOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-intercom", new IntercomOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-instagram", new InstagramOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-lever-hiring", new LeverOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-microsoft-teams", new MicrosoftTeamsOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-notion", new NotionOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-bing-ads", new MicrosoftBingAdsOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-pinterest", new PinterestOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-pipedrive", new PipeDriveOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-quickbooks", new QuickbooksOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-retently", new RetentlyOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-linkedin-ads", new LinkedinAdsOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-salesforce", new SalesforceOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-slack", new SlackOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-smartsheets", new SmartsheetsOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-snapchat-marketing", new SnapchatMarketingOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-square", new SquareOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-strava", new StravaOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-surveymonkey", new SurveymonkeyOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-trello", new TrelloOAuthFlow(configRepository))
        .put("yuanrui2014/source-youtube-analytics", new YouTubeAnalyticsOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-drift", new DriftOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-zendesk-chat", new ZendeskChatOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-zendesk-support", new ZendeskSupportOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-zendesk-talk", new ZendeskTalkOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-monday", new MondayOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-zendesk-sunshine", new ZendeskSunshineOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-mailchimp", new MailchimpOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-shopify", new ShopifyOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-tiktok-marketing", new TikTokMarketingOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/destination-snowflake", new DestinationSnowflakeOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/destination-google-sheets", new DestinationGoogleSheetsOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-snowflake", new SourceSnowflakeOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-okta", new OktaOAuthFlow(configRepository, httpClient))
        .put("yuanrui2014/source-paypal-transaction", new PayPalTransactionOAuthFlow(configRepository, httpClient))
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
