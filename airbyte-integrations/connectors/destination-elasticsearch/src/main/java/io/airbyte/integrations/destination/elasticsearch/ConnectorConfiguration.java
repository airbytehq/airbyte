package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.Objects;

@JsonIgnoreProperties(ignoreUnknown = true)
public class ConnectorConfiguration {

    private String host;
    private int port;
    private String apiKeyId;
    private String apiKeySecret;
    private boolean ssl;

    public ConnectorConfiguration() {}
    public static ConnectorConfiguration FromJsonNode(JsonNode config) {
        return new ObjectMapper().convertValue(config, ConnectorConfiguration.class);
    }

    public String getHost() {
        return this.host;
    }

    public int getPort() {
        return this.port;
    }

    public String getApiKeyId() {
        return this.apiKeyId;
    }

    public String getApiKeySecret() {
        return this.apiKeySecret;
    }

    public boolean isSsl() {
        return this.ssl;
    }

    public void setHost(String host) {
        this.host = host;
    }

    public void setPort(int port) {
        this.port = port;
    }

    public void setApiKeyId(String apiKeyId) {
        this.apiKeyId = apiKeyId;
    }

    public void setApiKeySecret(String apiKeySecret) {
        this.apiKeySecret = apiKeySecret;
    }

    public void setSsl(boolean ssl) {
        this.ssl = ssl;
    }

    public boolean equals(final Object o) {
        if (o == this) return true;
        if (!(o instanceof ConnectorConfiguration)) return false;
        final ConnectorConfiguration other = (ConnectorConfiguration) o;
        if (!other.canEqual(this)) return false;
        final Object this$host = this.getHost();
        final Object other$host = other.getHost();
        if (!Objects.equals(this$host, other$host)) return false;
        if (this.getPort() != other.getPort()) return false;
        final Object this$username = this.getApiKeyId();
        final Object other$username = other.getApiKeyId();
        if (!Objects.equals(this$username, other$username)) return false;
        final Object this$password = this.getApiKeySecret();
        final Object other$password = other.getApiKeySecret();
        if (!Objects.equals(this$password, other$password)) return false;
        return this.isSsl() == other.isSsl();
    }

    protected boolean canEqual(final Object other) {
        return other instanceof ConnectorConfiguration;
    }

    public int hashCode() {
        final int PRIME = 59;
        int result = 1;
        final Object $host = this.getHost();
        result = result * PRIME + ($host == null ? 43 : $host.hashCode());
        result = result * PRIME + this.getPort();
        final Object $username = this.getApiKeyId();
        result = result * PRIME + ($username == null ? 43 : $username.hashCode());
        final Object $password = this.getApiKeySecret();
        result = result * PRIME + ($password == null ? 43 : $password.hashCode());
        result = result * PRIME + (this.isSsl() ? 79 : 97);
        return result;
    }

    public String toString() {
        return "ConnectorConfiguration(host=" + this.getHost() + ", port=" + this.getPort() + ", username=" + this.getApiKeyId() + ", ssl=" + this.isSsl() + ")";
    }
}
