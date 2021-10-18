package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.Objects;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ConnectorConfiguration {

    private String endpoint;
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

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ConnectorConfiguration that = (ConnectorConfiguration) o;
        return Objects.equals(endpoint, that.endpoint) &&
                Objects.equals(username, that.username) &&
                Objects.equals(password, that.password) &&
                Objects.equals(apiKeyId, that.apiKeyId) &&
                Objects.equals(apiKeySecret, that.apiKeySecret);
    }

    @Override
    public int hashCode() {
        return Objects.hash(endpoint, username, password, apiKeyId, apiKeySecret);
    }

    @Override
    public String toString() {
        return "ConnectorConfiguration{" +
                "endpoint='" + endpoint + '\'' +
                ", username='" + username + '\'' +
                ", apiKeyId='" + apiKeyId + '\'' +
                '}';
    }
}
