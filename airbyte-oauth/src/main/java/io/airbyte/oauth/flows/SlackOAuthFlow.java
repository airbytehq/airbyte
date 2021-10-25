package io.airbyte.oauth.flows;

import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthFlow;
import org.apache.http.client.utils.URIBuilder;

import java.io.IOException;
import java.net.URISyntaxException;
import java.util.UUID;

public class SlackOAuthFlow extends BaseOAuthFlow {

  final String SLACK_CONSENT_URL_BASE = "https://slack.com/oauth/authorize";
  final String SLACK_TOKEN_URL = "https://slack.com/api/oauth.access";
  public SlackOAuthFlow(ConfigRepository configRepository) {
    super(configRepository);
  }

  /**
   * Depending on the OAuth flow implementation, the URL to grant user's consent may differ,
   * especially in the query parameters to be provided. This function should generate such consent URL
   * accordingly.
   *
   * @param definitionId
   * @param clientId
   * @param redirectUrl
   */
  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) throws IOException {
    try {
      return new URIBuilder(SLACK_CONSENT_URL_BASE)
              .addParameter("client_id", clientId)
              .addParameter("redirect_uri", redirectUrl)
              .addParameter("state", getState())
              .addParameter("scope", "read")
              .build().toString();
    } catch (URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  /**
   * Returns the URL where to retrieve the access token from.
   */
  @Override
  protected String getAccessTokenUrl() {
    return SLACK_TOKEN_URL;
  }
}
