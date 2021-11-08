/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthFlow;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

public class HubspotOAuthFlow extends BaseOAuthFlow {

  private final String AUTHORIZE_URL = "https://app.hubspot.com/oauth/authorize";

  public HubspotOAuthFlow(ConfigRepository configRepository, HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  public HubspotOAuthFlow(ConfigRepository configRepository, HttpClient httpClient, Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier, TOKEN_REQUEST_CONTENT_TYPE.JSON);
  }

  /**
   * Depending on the OAuth flow implementation, the URL to grant user's consent may differ,
   * especially in the query parameters to be provided. This function should generate such consent URL
   * accordingly.
   *
   * @param definitionId The configured definition ID of this client
   * @param clientId The configured client ID
   * @param redirectUrl the redirect URL
   */
  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) throws IOException {
    try {
      return new URIBuilder(AUTHORIZE_URL)
          .addParameter("client_id", clientId)
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("state", getState())
          .addParameter("scopes", getScopes())
          .build().toString();
    } catch (URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(String clientId, String clientSecret, String authCode, String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        // required
        .put("client_id", clientId)
        .put("redirect_uri", redirectUrl)
        .put("client_secret", clientSecret)
        .put("code", authCode)
        .put("grant_type", "authorization_code")
        .build();
  }

  private String getScopes() {
    return String.join(" ", "content",
        "crm.schemas.deals.read",
        "crm.objects.owners.read",
        "forms",
        "tickets",
        "e-commerce",
        "crm.objects.companies.read",
        "crm.lists.read",
        "crm.objects.deals.read",
        "crm.schemas.contacts.read",
        "crm.objects.contacts.read",
        "crm.schemas.companies.read",
        "files",
        "forms-uploaded-files",
        "files.ui_hidden.read");
  }

  /**
   * Returns the URL where to retrieve the access token from.
   *
   * @param oAuthParamConfig the configuration map
   */
  @Override
  protected String getAccessTokenUrl() {
    return "https://api.hubapi.com/oauth/v1/token";
  }

  @Override
  protected String getClientIdUnsafe(final JsonNode config) {
    // the config object containing client ID and secret is nested inside the "credentials" object
    Preconditions.checkArgument(config.hasNonNull("credentials"));
    return super.getClientIdUnsafe(config.get("credentials"));
  }

  @Override
  protected String getClientSecretUnsafe(final JsonNode config) {
    // the config object containing client ID and secret is nested inside the "credentials" object
    Preconditions.checkArgument(config.hasNonNull("credentials"));
    return super.getClientSecretUnsafe(config.get("credentials"));
  }

}
