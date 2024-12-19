
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.databind.JsonNode;
import java.io.Serializable;
import java.util.UUID;

/**
 * StandardCheckConnectionInput
 * <p>
 * information required for connection.
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "actorType",
    "actorId",
    "connectionConfiguration"
})
public class StandardCheckConnectionInput implements Serializable
{

    /**
     * ActorType
     * <p>
     * enum that describes different types of actors
     * 
     */
    @JsonProperty("actorType")
    @JsonPropertyDescription("enum that describes different types of actors")
    private ActorType actorType;
    /**
     * The ID of the actor being checked, so we can persist config updates
     * 
     */
    @JsonProperty("actorId")
    @JsonPropertyDescription("The ID of the actor being checked, so we can persist config updates")
    private UUID actorId;
    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     * 
     */
    @JsonProperty("connectionConfiguration")
    @JsonPropertyDescription("Integration specific blob. Must be a valid JSON string.")
    private JsonNode connectionConfiguration;
    private final static long serialVersionUID = 8678033101171962295L;

    /**
     * ActorType
     * <p>
     * enum that describes different types of actors
     * 
     */
    @JsonProperty("actorType")
    public ActorType getActorType() {
        return actorType;
    }

    /**
     * ActorType
     * <p>
     * enum that describes different types of actors
     * 
     */
    @JsonProperty("actorType")
    public void setActorType(ActorType actorType) {
        this.actorType = actorType;
    }

    public StandardCheckConnectionInput withActorType(ActorType actorType) {
        this.actorType = actorType;
        return this;
    }

    /**
     * The ID of the actor being checked, so we can persist config updates
     * 
     */
    @JsonProperty("actorId")
    public UUID getActorId() {
        return actorId;
    }

    /**
     * The ID of the actor being checked, so we can persist config updates
     * 
     */
    @JsonProperty("actorId")
    public void setActorId(UUID actorId) {
        this.actorId = actorId;
    }

    public StandardCheckConnectionInput withActorId(UUID actorId) {
        this.actorId = actorId;
        return this;
    }

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

    public StandardCheckConnectionInput withConnectionConfiguration(JsonNode connectionConfiguration) {
        this.connectionConfiguration = connectionConfiguration;
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(StandardCheckConnectionInput.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("actorType");
        sb.append('=');
        sb.append(((this.actorType == null)?"<null>":this.actorType));
        sb.append(',');
        sb.append("actorId");
        sb.append('=');
        sb.append(((this.actorId == null)?"<null>":this.actorId));
        sb.append(',');
        sb.append("connectionConfiguration");
        sb.append('=');
        sb.append(((this.connectionConfiguration == null)?"<null>":this.connectionConfiguration));
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
        result = ((result* 31)+((this.actorType == null)? 0 :this.actorType.hashCode()));
        result = ((result* 31)+((this.actorId == null)? 0 :this.actorId.hashCode()));
        result = ((result* 31)+((this.connectionConfiguration == null)? 0 :this.connectionConfiguration.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof StandardCheckConnectionInput) == false) {
            return false;
        }
        StandardCheckConnectionInput rhs = ((StandardCheckConnectionInput) other);
        return ((((this.actorType == rhs.actorType)||((this.actorType!= null)&&this.actorType.equals(rhs.actorType)))&&((this.actorId == rhs.actorId)||((this.actorId!= null)&&this.actorId.equals(rhs.actorId))))&&((this.connectionConfiguration == rhs.connectionConfiguration)||((this.connectionConfiguration!= null)&&this.connectionConfiguration.equals(rhs.connectionConfiguration))));
    }

}
