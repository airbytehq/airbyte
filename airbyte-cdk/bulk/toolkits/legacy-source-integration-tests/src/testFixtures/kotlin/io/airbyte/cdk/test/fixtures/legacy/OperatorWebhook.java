
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * OperatorWebhook
 * <p>
 * Settings for a webhook operation
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "executionUrl",
    "executionBody",
    "webhookConfigId"
})
public class OperatorWebhook implements Serializable
{

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("executionUrl")
    private String executionUrl;
    @JsonProperty("executionBody")
    private String executionBody;
    @JsonProperty("webhookConfigId")
    private UUID webhookConfigId;
    @JsonIgnore
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();
    private final static long serialVersionUID = 6156722361495187053L;

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("executionUrl")
    public String getExecutionUrl() {
        return executionUrl;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("executionUrl")
    public void setExecutionUrl(String executionUrl) {
        this.executionUrl = executionUrl;
    }

    public OperatorWebhook withExecutionUrl(String executionUrl) {
        this.executionUrl = executionUrl;
        return this;
    }

    @JsonProperty("executionBody")
    public String getExecutionBody() {
        return executionBody;
    }

    @JsonProperty("executionBody")
    public void setExecutionBody(String executionBody) {
        this.executionBody = executionBody;
    }

    public OperatorWebhook withExecutionBody(String executionBody) {
        this.executionBody = executionBody;
        return this;
    }

    @JsonProperty("webhookConfigId")
    public UUID getWebhookConfigId() {
        return webhookConfigId;
    }

    @JsonProperty("webhookConfigId")
    public void setWebhookConfigId(UUID webhookConfigId) {
        this.webhookConfigId = webhookConfigId;
    }

    public OperatorWebhook withWebhookConfigId(UUID webhookConfigId) {
        this.webhookConfigId = webhookConfigId;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperty(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    public OperatorWebhook withAdditionalProperty(String name, Object value) {
        this.additionalProperties.put(name, value);
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(OperatorWebhook.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("executionUrl");
        sb.append('=');
        sb.append(((this.executionUrl == null)?"<null>":this.executionUrl));
        sb.append(',');
        sb.append("executionBody");
        sb.append('=');
        sb.append(((this.executionBody == null)?"<null>":this.executionBody));
        sb.append(',');
        sb.append("webhookConfigId");
        sb.append('=');
        sb.append(((this.webhookConfigId == null)?"<null>":this.webhookConfigId));
        sb.append(',');
        sb.append("additionalProperties");
        sb.append('=');
        sb.append(((this.additionalProperties == null)?"<null>":this.additionalProperties));
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
        result = ((result* 31)+((this.webhookConfigId == null)? 0 :this.webhookConfigId.hashCode()));
        result = ((result* 31)+((this.additionalProperties == null)? 0 :this.additionalProperties.hashCode()));
        result = ((result* 31)+((this.executionUrl == null)? 0 :this.executionUrl.hashCode()));
        result = ((result* 31)+((this.executionBody == null)? 0 :this.executionBody.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof OperatorWebhook) == false) {
            return false;
        }
        OperatorWebhook rhs = ((OperatorWebhook) other);
        return (((((this.webhookConfigId == rhs.webhookConfigId)||((this.webhookConfigId!= null)&&this.webhookConfigId.equals(rhs.webhookConfigId)))&&((this.additionalProperties == rhs.additionalProperties)||((this.additionalProperties!= null)&&this.additionalProperties.equals(rhs.additionalProperties))))&&((this.executionUrl == rhs.executionUrl)||((this.executionUrl!= null)&&this.executionUrl.equals(rhs.executionUrl))))&&((this.executionBody == rhs.executionBody)||((this.executionBody!= null)&&this.executionBody.equals(rhs.executionBody))));
    }

}
