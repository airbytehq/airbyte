
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.Serializable;
import java.util.UUID;

/**
 * WorkerDestinationConfig
 * <p>
 * WorkerDestinationConfig
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "destinationId",
    "destinationConnectionConfiguration",
    "catalog",
    "connectionId",
    "state"
})
public class WorkerDestinationConfig implements Serializable
{

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("destinationId")
    private UUID destinationId;
    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     * 
     */
    @JsonProperty("destinationConnectionConfiguration")
    @JsonPropertyDescription("Integration specific blob. Must be a valid JSON string.")
    private JsonNode destinationConnectionConfiguration;
    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("catalog")
    private ConfiguredAirbyteCatalog catalog;
    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("connectionId")
    private UUID connectionId;
    /**
     * State
     * <p>
     * information output by the connection.
     * 
     */
    @JsonProperty("state")
    @JsonPropertyDescription("information output by the connection.")
    private State state;
    private final static long serialVersionUID = 4991217442954865951L;

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("destinationId")
    public UUID getDestinationId() {
        return destinationId;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("destinationId")
    public void setDestinationId(UUID destinationId) {
        this.destinationId = destinationId;
    }

    public WorkerDestinationConfig withDestinationId(UUID destinationId) {
        this.destinationId = destinationId;
        return this;
    }

    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     * 
     */
    @JsonProperty("destinationConnectionConfiguration")
    public JsonNode getDestinationConnectionConfiguration() {
        return destinationConnectionConfiguration;
    }

    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     * 
     */
    @JsonProperty("destinationConnectionConfiguration")
    public void setDestinationConnectionConfiguration(JsonNode destinationConnectionConfiguration) {
        this.destinationConnectionConfiguration = destinationConnectionConfiguration;
    }

    public WorkerDestinationConfig withDestinationConnectionConfiguration(JsonNode destinationConnectionConfiguration) {
        this.destinationConnectionConfiguration = destinationConnectionConfiguration;
        return this;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("catalog")
    public ConfiguredAirbyteCatalog getCatalog() {
        return catalog;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("catalog")
    public void setCatalog(ConfiguredAirbyteCatalog catalog) {
        this.catalog = catalog;
    }

    public WorkerDestinationConfig withCatalog(ConfiguredAirbyteCatalog catalog) {
        this.catalog = catalog;
        return this;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("connectionId")
    public UUID getConnectionId() {
        return connectionId;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("connectionId")
    public void setConnectionId(UUID connectionId) {
        this.connectionId = connectionId;
    }

    public WorkerDestinationConfig withConnectionId(UUID connectionId) {
        this.connectionId = connectionId;
        return this;
    }

    /**
     * State
     * <p>
     * information output by the connection.
     * 
     */
    @JsonProperty("state")
    public State getState() {
        return state;
    }

    /**
     * State
     * <p>
     * information output by the connection.
     * 
     */
    @JsonProperty("state")
    public void setState(State state) {
        this.state = state;
    }

    public WorkerDestinationConfig withState(State state) {
        this.state = state;
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(WorkerDestinationConfig.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("destinationId");
        sb.append('=');
        sb.append(((this.destinationId == null)?"<null>":this.destinationId));
        sb.append(',');
        sb.append("destinationConnectionConfiguration");
        sb.append('=');
        sb.append(((this.destinationConnectionConfiguration == null)?"<null>":this.destinationConnectionConfiguration));
        sb.append(',');
        sb.append("catalog");
        sb.append('=');
        sb.append(((this.catalog == null)?"<null>":this.catalog));
        sb.append(',');
        sb.append("connectionId");
        sb.append('=');
        sb.append(((this.connectionId == null)?"<null>":this.connectionId));
        sb.append(',');
        sb.append("state");
        sb.append('=');
        sb.append(((this.state == null)?"<null>":this.state));
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
        result = ((result* 31)+((this.connectionId == null)? 0 :this.connectionId.hashCode()));
        result = ((result* 31)+((this.state == null)? 0 :this.state.hashCode()));
        result = ((result* 31)+((this.destinationId == null)? 0 :this.destinationId.hashCode()));
        result = ((result* 31)+((this.destinationConnectionConfiguration == null)? 0 :this.destinationConnectionConfiguration.hashCode()));
        result = ((result* 31)+((this.catalog == null)? 0 :this.catalog.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof WorkerDestinationConfig) == false) {
            return false;
        }
        WorkerDestinationConfig rhs = ((WorkerDestinationConfig) other);
        return ((((((this.connectionId == rhs.connectionId)||((this.connectionId!= null)&&this.connectionId.equals(rhs.connectionId)))&&((this.state == rhs.state)||((this.state!= null)&&this.state.equals(rhs.state))))&&((this.destinationId == rhs.destinationId)||((this.destinationId!= null)&&this.destinationId.equals(rhs.destinationId))))&&((this.destinationConnectionConfiguration == rhs.destinationConnectionConfiguration)||((this.destinationConnectionConfiguration!= null)&&this.destinationConnectionConfiguration.equals(rhs.destinationConnectionConfiguration))))&&((this.catalog == rhs.catalog)||((this.catalog!= null)&&this.catalog.equals(rhs.catalog))));
    }

}
