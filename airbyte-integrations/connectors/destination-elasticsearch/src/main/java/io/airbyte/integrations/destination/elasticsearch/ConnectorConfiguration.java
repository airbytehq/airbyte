package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.Objects;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ConnectorConfiguration {

    private String endpoint;
    private int port;
    private String username;
    private String password;
    private String apiKeyId;
    private String apiKeySecret;

    public ConnectorConfiguration() {
    }

    public static ConnectorConfiguration FromJsonNode(JsonNode config) {
        return new ObjectMapper().convertValue(config, ConnectorConfiguration.class);
    }

    public String getEndpoint() {
        return this.endpoint;
    }

    public String getApiKeyId() {
        return this.apiKeyId;
    }

    public String getUsername() {
        return this.username;
    }

    public String getPassword() {
        return this.password;
    }

    public String getApiKeySecret() {
        return this.apiKeySecret;
    }


    public void setEndpoint(String endpoint) {
        this.endpoint = endpoint;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public void setApiKeyId(String apiKeyId) {
        this.apiKeyId = apiKeyId;
    }

    public void setApiKeySecret(String apiKeySecret) {
        this.apiKeySecret = apiKeySecret;
    }

    public boolean isUsingBasicAuth() {
        return Objects.nonNull(this.username) &&
                !this.username.isEmpty() &&
                Objects.nonNull(this.password) &&
                !this.password.isEmpty();
    }

    public boolean isUsingApiKey() {
        return Objects.nonNull(this.apiKeyId) &&
                !this.apiKeyId.isEmpty() &&
                Objects.nonNull(this.apiKeySecret) &&
                !this.apiKeySecret.isEmpty();
    }


    public boolean equals(final Object o) {
        if (o == this) return true;
        if (!(o instanceof ConnectorConfiguration)) return false;
        final ConnectorConfiguration other = (ConnectorConfiguration) o;
        if (!other.canEqual(this)) return false;
        final Object this$host = this.getEndpoint();
        final Object other$host = other.getEndpoint();
        if (!Objects.equals(this$host, other$host)) return false;
        final Object this$username = this.getApiKeyId();
        final Object other$username = other.getApiKeyId();
        if (!Objects.equals(this$username, other$username)) return false;
        final Object this$password = this.getApiKeySecret();
        final Object other$password = other.getApiKeySecret();
        if (!Objects.equals(this$password, other$password)) return false;
        return true;
    }

    protected boolean canEqual(final Object other) {
        return other instanceof ConnectorConfiguration;
    }

    public int hashCode() {
        final int PRIME = 59;
        int result = 1;
        final Object $host = this.getEndpoint();
        result = result * PRIME + ($host == null ? 43 : $host.hashCode());
        final Object $username = this.getApiKeyId();
        result = result * PRIME + ($username == null ? 43 : $username.hashCode());
        final Object $password = this.getApiKeySecret();
        result = result * PRIME + ($password == null ? 43 : $password.hashCode());
        return result;
    }

    public String toString() {
        return "ConnectorConfiguration(endpoint=" + this.getEndpoint() + ", username=" + this.getApiKeyId() + ")";
    }
}
