/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuth2Flow;
import io.airbyte.protocol.models.OAuthConfigSpecification;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import lombok.extern.slf4j.Slf4j;
import org.apache.http.client.utils.URIBuilder;

@Slf4j
public class AmazonSellerPartnerOAuthFlow extends BaseOAuth2Flow {

  private static final String EU_AUTH_URL = "sellercentral-europe.amazon.com";

  enum RegionHost {

    /**
     *
     */
    AE("sellercentral.amazon.ae"),
    DE(EU_AUTH_URL),
    PL("sellercentral.amazon.pl"),
    EG("sellercentral.amazon.eg"),
    ES(EU_AUTH_URL),
    FR(EU_AUTH_URL),
    IN("sellercentral.amazon.in"),
    IT(EU_AUTH_URL),
    NL("sellercentral.amazon.nl"),
    SA("sellercentral.amazon.sa"),
    SE("sellercentral.amazon.se"),
    TR("sellercentral.amazon.com.tr"),
    UK(EU_AUTH_URL),

    AU("sellercentral.amazon.com.au"),
    JP("sellercentral.amazon.co.jp"),
    SG("sellercentral.amazon.sg"),

    US("sellercentral.amazon.com"),
    BR("sellercentral.amazon.com.br"),
    CA("sellercentral.amazon.ca"),
    MX("sellercentral.amazon.com.mx"),
    BE("sellercentral.amazon.com.be"),
    ;

    private final String host;

    RegionHost(String host) {
      this.host = host;
    }

    public String getHost() {
      return host;
    }

  }

  private static final String AUTHORIZE_URL = "https://sellercentral.amazon.com/apps/authorize/consent";
  private static final String ACCESS_TOKEN_URL = "https://api.amazon.com/auth/o2/token";

  @Override
  protected String getClientIdUnsafe(final JsonNode oauthConfig) {
    return getConfigValueUnsafe(oauthConfig, "lwa_app_id");
  }

  @Override
  protected String getClientSecretUnsafe(final JsonNode oauthConfig) {
    return getConfigValueUnsafe(oauthConfig, "lwa_client_secret");
  }

  public AmazonSellerPartnerOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  public AmazonSellerPartnerOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
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
  protected String formatConsentUrl(final UUID definitionId,
                                    final String clientId,
                                    final String redirectUrl,
                                    final JsonNode inputOAuthConfiguration)
          throws IOException {

    // getting application_id value from user's config
    final String application_id = getConfigValueUnsafe(inputOAuthConfiguration, "app_id");

    try {
      return new URIBuilder(AUTHORIZE_URL)
              .addParameter("application_id", application_id)
              .addParameter("redirect_uri", redirectUrl)
              .addParameter("state", getState())
              .addParameter("version", "beta")
              .build().toString();
    } catch (final URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected String extractCodeParameter(final Map<String, Object> queryParams) throws IOException {
    if (queryParams.containsKey("spapi_oauth_code")) {
      return (String) queryParams.get("spapi_oauth_code");
    } else {
      throw new IOException("Undefined 'spapi_oauth_code' from consent redirected url.");
    }
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(final String clientId,
                                                              final String clientSecret,
                                                              final String authCode,
                                                              final String redirectUrl) {
    return ImmutableMap.<String, String>builder()
            // required
            .put("client_id", clientId)
            .put("redirect_uri", redirectUrl)
            .put("client_secret", clientSecret)
            .put("code", authCode)
            .put("grant_type", "authorization_code")
            .build();
  }

  /**
   * Returns the URL where to retrieve the access token from.
   *
   */
  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    return ACCESS_TOKEN_URL;
  }

  @Override
  public List<String> getDefaultOAuthOutputPath() {
    return List.of();
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
  protected String formatConsentUrl_new(final UUID definitionId,
                                        final String clientId,
                                        final String redirectUrl,
                                        final JsonNode inputOAuthConfiguration,
                                        JsonNode oAuthParamConfig)
          throws IOException {
    // getting application_id value from user's config
    final String application_id = getConfigValueUnsafe(oAuthParamConfig, "app_id");
    final String regionCountry = getConfigValueUnsafe(inputOAuthConfiguration, "region");
    String authUrl = RegionHost.valueOf(regionCountry).getHost();
    log.info("authUrl: {}", authUrl);

    String newAuthUrl = String.format("https://%s/apps/authorize/consent", authUrl);
    try {
      return new URIBuilder(newAuthUrl)
              .addParameter("application_id", application_id)
              .addParameter("redirect_uri", redirectUrl)
              .addParameter("state", getState())
              .addParameter("version", "beta")
              .build().toString();
    } catch (final URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  public String getSourceConsentUrl(final UUID workspaceId,
                                    final UUID sourceDefinitionId,
                                    final String redirectUrl,
                                    final JsonNode inputOAuthConfiguration,
                                    final OAuthConfigSpecification oAuthConfigSpecification)
          throws IOException, ConfigNotFoundException, JsonValidationException {
    validateInputOAuthConfiguration(oAuthConfigSpecification, inputOAuthConfiguration);
    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);

    log.info("oAuthParamConfig: {}", oAuthParamConfig);
    if (multiParameterAuth) {
      return formatConsentUrl_new(sourceDefinitionId,
              getClientIdUnsafe(oAuthParamConfig),
              getConfigValueUnsafe(oAuthParamConfig, "redirect_url"),
              inputOAuthConfiguration,
              oAuthParamConfig);
    }
    return formatConsentUrl_new(sourceDefinitionId,
            getClientIdUnsafe(oAuthParamConfig),
            redirectUrl,
            inputOAuthConfiguration,
            oAuthParamConfig);
  }

}