package io.airbyte.oauth.flows.zendesk;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthFlow;
import io.airbyte.oauth.OAuthFlowImplementation;

import java.io.IOException;
import java.net.http.HttpClient;
import java.text.MessageFormat;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;

public class ZendeskOAuthFlow extends BaseOAuthFlow {

    private String subdomain;

    public ZendeskOAuthFlow(ConfigRepository configRepository, HttpClient httpClient, Supplier<String> stateSupplier) {
        super(configRepository, httpClient, stateSupplier);
    }

    public ZendeskOAuthFlow(ConfigRepository configRepository) {
        super(configRepository);

    }

    protected String getSubdomainUnsafe(JsonNode oauthConfig) {
        if (oauthConfig.get("subdomain") != null) {
            return oauthConfig.get("subdomain").asText();
        } else {
            throw new IllegalArgumentException("Undefined parameter 'subdomain' necessary for the Zendesk OAuth Flow.");
        }
    }


    @Override
    public String getSourceConsentUrl(UUID workspaceId, UUID sourceDefinitionId, String redirectUrl) throws IOException, ConfigNotFoundException {
        final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
        // see comment on completeSourceOAuth
        return formatConsentUrl(null, getClientIdUnsafe(oAuthParamConfig), redirectUrl, MessageFormat.format("{0}.zendesk.com", getSubdomainUnsafe(oAuthParamConfig)),
                "oauth/authorizations/new", "read", "code");
    }


    protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) throws IOException {
        return null;
    }

    @Override
    public Map<String, Object> completeSourceOAuth(UUID workspaceId, UUID sourceDefinitionId, Map<String, Object> queryParams, String redirectUrl) throws IOException, ConfigNotFoundException {
        final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
        // Temporary workaround. We need the subdomain to build the URL, the subdomoin is on config, to get the config we need the workspaceId and sourceDefinitionId
        // an alternative would be to add those two itens as instance fields.
        subdomain = getSubdomainUnsafe(oAuthParamConfig);
        return super.completeSourceOAuth(workspaceId,sourceDefinitionId, queryParams, redirectUrl);

    }


    /**
     * Returns the URL where to retrieve the access token from.
     */
    @Override
    protected String getAccessTokenUrl() {
        // see comment on completeSourceOAuth
        return MessageFormat.format("https://{0}.zendesk.com/oauth/tokens", subdomain);
    }

    /**
     * Query parameters to provide the access token url with.
     *
     * @param clientId
     * @param clientSecret
     * @param authCode
     * @param redirectUrl
     */
    @Override
    protected Map<String, String> getAccessTokenQueryParameters(String clientId, String clientSecret, String authCode, String redirectUrl) {
        return ImmutableMap.<String, String>builder()
                // required
                .put("client_id", clientId)
                .put("redirect_uri", redirectUrl)
                .put("client_secret", clientSecret)
                .put("grant_type", "authorization_code")
                .put("code", authCode)
                .build();
    }

    protected Map<String, Object> extractRefreshToken(JsonNode data) throws IOException {
        // Facebook does not have refresh token but calls it "long lived access token" instead:
        // see https://developers.facebook.com/docs/facebook-login/access-tokens/refreshing
        if (data.has("access_token")) {
            return Map.of("access_token", data.get("access_token").asText());
        } else {
            throw new IOException(String.format("Missing 'access_token' in query params from %s", getAccessTokenUrl()));
        }
    }
}
