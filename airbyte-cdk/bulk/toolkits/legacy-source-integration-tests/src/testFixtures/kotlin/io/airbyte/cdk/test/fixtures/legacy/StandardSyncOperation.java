
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.annotation.JsonValue;
import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * StandardSyncOperation
 * <p>
 * Configuration of an operation to apply during a sync
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "operationId",
    "name",
    "operatorType",
    "operatorNormalization",
    "operatorDbt",
    "operatorWebhook",
    "tombstone",
    "workspaceId"
})
public class StandardSyncOperation implements Serializable
{

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("operationId")
    private UUID operationId;
    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("name")
    private String name;
    /**
     * OperatorType
     * <p>
     * Type of Operator
     * (Required)
     * 
     */
    @JsonProperty("operatorType")
    @JsonPropertyDescription("Type of Operator")
    private OperatorType operatorType;
    /**
     * OperatorNormalization
     * <p>
     * Settings for a normalization operator
     * 
     */
    @JsonProperty("operatorNormalization")
    @JsonPropertyDescription("Settings for a normalization operator")
    private OperatorNormalization operatorNormalization;
    /**
     * OperatorDbt
     * <p>
     * Settings for a DBT operator
     * 
     */
    @JsonProperty("operatorDbt")
    @JsonPropertyDescription("Settings for a DBT operator")
    private OperatorDbt operatorDbt;
    /**
     * OperatorWebhook
     * <p>
     * Settings for a webhook operation
     * 
     */
    @JsonProperty("operatorWebhook")
    @JsonPropertyDescription("Settings for a webhook operation")
    private OperatorWebhook operatorWebhook;
    /**
     * if not set or false, the configuration is active. if true, then this configuration is permanently off.
     * 
     */
    @JsonProperty("tombstone")
    @JsonPropertyDescription("if not set or false, the configuration is active. if true, then this configuration is permanently off.")
    private Boolean tombstone;
    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("workspaceId")
    private UUID workspaceId;
    private final static long serialVersionUID = 1883842093468364803L;

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("operationId")
    public UUID getOperationId() {
        return operationId;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("operationId")
    public void setOperationId(UUID operationId) {
        this.operationId = operationId;
    }

    public StandardSyncOperation withOperationId(UUID operationId) {
        this.operationId = operationId;
        return this;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("name")
    public String getName() {
        return name;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("name")
    public void setName(String name) {
        this.name = name;
    }

    public StandardSyncOperation withName(String name) {
        this.name = name;
        return this;
    }

    /**
     * OperatorType
     * <p>
     * Type of Operator
     * (Required)
     * 
     */
    @JsonProperty("operatorType")
    public OperatorType getOperatorType() {
        return operatorType;
    }

    /**
     * OperatorType
     * <p>
     * Type of Operator
     * (Required)
     * 
     */
    @JsonProperty("operatorType")
    public void setOperatorType(OperatorType operatorType) {
        this.operatorType = operatorType;
    }

    public StandardSyncOperation withOperatorType(OperatorType operatorType) {
        this.operatorType = operatorType;
        return this;
    }

    /**
     * OperatorNormalization
     * <p>
     * Settings for a normalization operator
     * 
     */
    @JsonProperty("operatorNormalization")
    public OperatorNormalization getOperatorNormalization() {
        return operatorNormalization;
    }

    /**
     * OperatorNormalization
     * <p>
     * Settings for a normalization operator
     * 
     */
    @JsonProperty("operatorNormalization")
    public void setOperatorNormalization(OperatorNormalization operatorNormalization) {
        this.operatorNormalization = operatorNormalization;
    }

    public StandardSyncOperation withOperatorNormalization(OperatorNormalization operatorNormalization) {
        this.operatorNormalization = operatorNormalization;
        return this;
    }

    /**
     * OperatorDbt
     * <p>
     * Settings for a DBT operator
     * 
     */
    @JsonProperty("operatorDbt")
    public OperatorDbt getOperatorDbt() {
        return operatorDbt;
    }

    /**
     * OperatorDbt
     * <p>
     * Settings for a DBT operator
     * 
     */
    @JsonProperty("operatorDbt")
    public void setOperatorDbt(OperatorDbt operatorDbt) {
        this.operatorDbt = operatorDbt;
    }

    public StandardSyncOperation withOperatorDbt(OperatorDbt operatorDbt) {
        this.operatorDbt = operatorDbt;
        return this;
    }

    /**
     * OperatorWebhook
     * <p>
     * Settings for a webhook operation
     * 
     */
    @JsonProperty("operatorWebhook")
    public OperatorWebhook getOperatorWebhook() {
        return operatorWebhook;
    }

    /**
     * OperatorWebhook
     * <p>
     * Settings for a webhook operation
     * 
     */
    @JsonProperty("operatorWebhook")
    public void setOperatorWebhook(OperatorWebhook operatorWebhook) {
        this.operatorWebhook = operatorWebhook;
    }

    public StandardSyncOperation withOperatorWebhook(OperatorWebhook operatorWebhook) {
        this.operatorWebhook = operatorWebhook;
        return this;
    }

    /**
     * if not set or false, the configuration is active. if true, then this configuration is permanently off.
     * 
     */
    @JsonProperty("tombstone")
    public Boolean getTombstone() {
        return tombstone;
    }

    /**
     * if not set or false, the configuration is active. if true, then this configuration is permanently off.
     * 
     */
    @JsonProperty("tombstone")
    public void setTombstone(Boolean tombstone) {
        this.tombstone = tombstone;
    }

    public StandardSyncOperation withTombstone(Boolean tombstone) {
        this.tombstone = tombstone;
        return this;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("workspaceId")
    public UUID getWorkspaceId() {
        return workspaceId;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("workspaceId")
    public void setWorkspaceId(UUID workspaceId) {
        this.workspaceId = workspaceId;
    }

    public StandardSyncOperation withWorkspaceId(UUID workspaceId) {
        this.workspaceId = workspaceId;
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(StandardSyncOperation.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("operationId");
        sb.append('=');
        sb.append(((this.operationId == null)?"<null>":this.operationId));
        sb.append(',');
        sb.append("name");
        sb.append('=');
        sb.append(((this.name == null)?"<null>":this.name));
        sb.append(',');
        sb.append("operatorType");
        sb.append('=');
        sb.append(((this.operatorType == null)?"<null>":this.operatorType));
        sb.append(',');
        sb.append("operatorNormalization");
        sb.append('=');
        sb.append(((this.operatorNormalization == null)?"<null>":this.operatorNormalization));
        sb.append(',');
        sb.append("operatorDbt");
        sb.append('=');
        sb.append(((this.operatorDbt == null)?"<null>":this.operatorDbt));
        sb.append(',');
        sb.append("operatorWebhook");
        sb.append('=');
        sb.append(((this.operatorWebhook == null)?"<null>":this.operatorWebhook));
        sb.append(',');
        sb.append("tombstone");
        sb.append('=');
        sb.append(((this.tombstone == null)?"<null>":this.tombstone));
        sb.append(',');
        sb.append("workspaceId");
        sb.append('=');
        sb.append(((this.workspaceId == null)?"<null>":this.workspaceId));
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
        result = ((result* 31)+((this.operatorDbt == null)? 0 :this.operatorDbt.hashCode()));
        result = ((result* 31)+((this.operatorWebhook == null)? 0 :this.operatorWebhook.hashCode()));
        result = ((result* 31)+((this.tombstone == null)? 0 :this.tombstone.hashCode()));
        result = ((result* 31)+((this.name == null)? 0 :this.name.hashCode()));
        result = ((result* 31)+((this.operationId == null)? 0 :this.operationId.hashCode()));
        result = ((result* 31)+((this.operatorNormalization == null)? 0 :this.operatorNormalization.hashCode()));
        result = ((result* 31)+((this.operatorType == null)? 0 :this.operatorType.hashCode()));
        result = ((result* 31)+((this.workspaceId == null)? 0 :this.workspaceId.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof StandardSyncOperation) == false) {
            return false;
        }
        StandardSyncOperation rhs = ((StandardSyncOperation) other);
        return (((((((((this.operatorDbt == rhs.operatorDbt)||((this.operatorDbt!= null)&&this.operatorDbt.equals(rhs.operatorDbt)))&&((this.operatorWebhook == rhs.operatorWebhook)||((this.operatorWebhook!= null)&&this.operatorWebhook.equals(rhs.operatorWebhook))))&&((this.tombstone == rhs.tombstone)||((this.tombstone!= null)&&this.tombstone.equals(rhs.tombstone))))&&((this.name == rhs.name)||((this.name!= null)&&this.name.equals(rhs.name))))&&((this.operationId == rhs.operationId)||((this.operationId!= null)&&this.operationId.equals(rhs.operationId))))&&((this.operatorNormalization == rhs.operatorNormalization)||((this.operatorNormalization!= null)&&this.operatorNormalization.equals(rhs.operatorNormalization))))&&((this.operatorType == rhs.operatorType)||((this.operatorType!= null)&&this.operatorType.equals(rhs.operatorType))))&&((this.workspaceId == rhs.workspaceId)||((this.workspaceId!= null)&&this.workspaceId.equals(rhs.workspaceId))));
    }


    /**
     * OperatorType
     * <p>
     * Type of Operator
     * 
     */
    public enum OperatorType {

        NORMALIZATION("normalization"),
        DBT("dbt"),
        WEBHOOK("webhook");
        private final String value;
        private final static Map<String, OperatorType> CONSTANTS = new HashMap<String, OperatorType>();

        static {
            for (OperatorType c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        private OperatorType(String value) {
            this.value = value;
        }

        @Override
        public String toString() {
            return this.value;
        }

        @JsonValue
        public String value() {
            return this.value;
        }

        @JsonCreator
        public static OperatorType fromValue(String value) {
            OperatorType constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

}
