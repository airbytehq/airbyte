package io.airbyte.oauth.flows;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthFlow;
import org.apache.http.client.utils.URIBuilder;

import java.io.IOException;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.util.UUID;
import java.util.function.Supplier;

public class LeverOAuthFlow extends BaseOAuthFlow {


  private static final String AUTHORIZE_URL = "https://sandbox-lever.auth0.com/authorize";
  private static final String ACCESS_TOKEN_URL = "https://sandbox-lever.auth0.com/oauth/token";
  private static final String SCOPES = String.join("+", "applications:read:admin",
          "audit_events:read:admin",
          "contact:read:admin",
          "feedback:read:admin",
          "feedback_templates:read:admin",
          "files:read:admin",
          "form_templates:read:admin",
          "forms:read:admin",
          "interviews:read:admin",
          "notes:read:admin",
          "offers:read:admin",
          "opportunities:read:admin",
          "postings:read:admin",
          "referrals:read:admin",
          "requisition_fields:read:admin",
          "requisitions:read:admin",
          "resumes:read:admin",
          "sources:read:admin",
          "stages:read:admin",
          "tasks:read:admin");

  private String getAudience() {
    return "https://api.sandbox.lever.co/v1/";
  }

  protected String formatOAuthConsentURL(
          String clientId,
          String redirectUrl,
          String state,
          String scope,
          String audience) throws URISyntaxException {
    URIBuilder builder = new URIBuilder(AUTHORIZE_URL);
    builder.addParameter("client_id", clientId);
    builder.addParameter("redirect_uri", redirectUrl);
    builder.addParameter("response_type", "code");
    builder.addParameter("state", state);
    builder.addParameter("scope", scope);
    builder.addParameter("prompt", "consent");
    builder.addParameter("audience", audience);
    return builder.toString();
  }

  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) throws IOException {
    return String.format("%s?client_id=%s&redirect_uri=%s&response_type=code&state=%s&scope=%s&prompt=consent&audience=%s",
            AUTHORIZE_URL,
            clientId,
            redirectUrl,
            getState(),
            "",
            getAudience());
  }

  public LeverOAuthFlow(ConfigRepository configRepository) {
    super(configRepository);
  }


  @VisibleForTesting
  LeverOAuthFlow(ConfigRepository configRepository, HttpClient httpClient, Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  /**
   * Returns the URL where to retrieve the access token from.
   */
  @Override
  protected String getAccessTokenUrl() {
    return ACCESS_TOKEN_URL;
  }
}
