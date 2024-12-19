
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.databind.JsonNode;
import java.io.Serializable;

/**
 * StandardDiscoverCatalogInput
 * <p>
 * information required for connection.
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "connectionConfiguration",
    "sourceId",
    "connectorVersion",
    "configHash"
})
public class StandardDiscoverCatalogInput implements Serializable
{

    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     * 
     */
    @JsonProperty("connectionConfiguration")
    @JsonPropertyDescription("Integration specific blob. Must be a valid JSON string.")
    private JsonNode connectionConfiguration;
    /**
     * The ID of the source being discovered, so we can persist the result
     * (Required)
     * 
     */
    @JsonProperty("sourceId")
    @JsonPropertyDescription("The ID of the source being discovered, so we can persist the result")
    private String sourceId;
    /**
     * Connector version, so we can persist the result
     * (Required)
     * 
     */
    @JsonProperty("connectorVersion")
    @JsonPropertyDescription("Connector version, so we can persist the result")
    private String connectorVersion;
    /**
     * Config hash, so we can persist the result
     * (Required)
     * 
     */
    @JsonProperty("configHash")
    @JsonPropertyDescription("Config hash, so we can persist the result")
    private String configHash;
    private final static long serialVersionUID = 6835276481871177055L;

    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     * 
     */
    @JsonProperty("connectionConfiguration")
    public JsonNode getConnectionConfiguration() {
        return connectionConfiguration;
    }

    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     * 
     */
    @JsonProperty("connectionConfiguration")
    public void setConnectionConfiguration(JsonNode connectionConfiguration) {
        this.connectionConfiguration = connectionConfiguration;
    }

    public StandardDiscoverCatalogInput withConnectionConfiguration(JsonNode connectionConfiguration) {
        this.connectionConfiguration = connectionConfiguration;
        return this;
    }

    /**
     * The ID of the source being discovered, so we can persist the result
     * (Required)
     * 
     */
    @JsonProperty("sourceId")
    public String getSourceId() {
        return sourceId;
    }

    /**
     * The ID of the source being discovered, so we can persist the result
     * (Required)
     * 
     */
    @JsonProperty("sourceId")
    public void setSourceId(String sourceId) {
        this.sourceId = sourceId;
    }

    public StandardDiscoverCatalogInput withSourceId(String sourceId) {
        this.sourceId = sourceId;
        return this;
    }

    /**
     * Connector version, so we can persist the result
     * (Required)
     * 
     */
    @JsonProperty("connectorVersion")
    public String getConnectorVersion() {
        return connectorVersion;
    }

    /**
     * Connector version, so we can persist the result
     * (Required)
     * 
     */
    @JsonProperty("connectorVersion")
    public void setConnectorVersion(String connectorVersion) {
        this.connectorVersion = connectorVersion;
    }

    public StandardDiscoverCatalogInput withConnectorVersion(String connectorVersion) {
        this.connectorVersion = connectorVersion;
        return this;
    }

    /**
     * Config hash, so we can persist the result
     * (Required)
     * 
     */
    @JsonProperty("configHash")
    public String getConfigHash() {
        return configHash;
    }

    /**
     * Config hash, so we can persist the result
     * (Required)
     * 
     */
    @JsonProperty("configHash")
    public void setConfigHash(String configHash) {
        this.configHash = configHash;
    }

    public StandardDiscoverCatalogInput withConfigHash(String configHash) {
        this.configHash = configHash;
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(StandardDiscoverCatalogInput.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("connectionConfiguration");
        sb.append('=');
        sb.append(((this.connectionConfiguration == null)?"<null>":this.connectionConfiguration));
        sb.append(',');
        sb.append("sourceId");
        sb.append('=');
        sb.append(((this.sourceId == null)?"<null>":this.sourceId));
        sb.append(',');
        sb.append("connectorVersion");
        sb.append('=');
        sb.append(((this.connectorVersion == null)?"<null>":this.connectorVersion));
        sb.append(',');
        sb.append("configHash");
        sb.append('=');
        sb.append(((this.configHash == null)?"<null>":this.configHash));
        sb.append(',');
        if (sb.charAt((sb.length()- 1)) == ',') {
            sb.setCharAt((sb.length()- 1), ']');
        } else {
            sb.append(']');
        }
        return sb.toString();
    }

    @Override
    public int hashCode() {
        int result = 1;
        result = ((result* 31)+((this.sourceId == null)? 0 :this.sourceId.hashCode()));
        result = ((result* 31)+((this.connectorVersion == null)? 0 :this.connectorVersion.hashCode()));
        result = ((result* 31)+((this.configHash == null)? 0 :this.configHash.hashCode()));
        result = ((result* 31)+((this.connectionConfiguration == null)? 0 :this.connectionConfiguration.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof StandardDiscoverCatalogInput) == false) {
            return false;
        }
        StandardDiscoverCatalogInput rhs = ((StandardDiscoverCatalogInput) other);
        return (((((this.sourceId == rhs.sourceId)||((this.sourceId!= null)&&this.sourceId.equals(rhs.sourceId)))&&((this.connectorVersion == rhs.connectorVersion)||((this.connectorVersion!= null)&&this.connectorVersion.equals(rhs.connectorVersion))))&&((this.configHash == rhs.configHash)||((this.configHash!= null)&&this.configHash.equals(rhs.configHash))))&&((this.connectionConfiguration == rhs.connectionConfiguration)||((this.connectionConfiguration!= null)&&this.connectionConfiguration.equals(rhs.connectionConfiguration))));
    }

}
