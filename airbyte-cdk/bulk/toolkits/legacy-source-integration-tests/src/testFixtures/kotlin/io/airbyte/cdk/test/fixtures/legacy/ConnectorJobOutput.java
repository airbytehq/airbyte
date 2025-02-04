
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.annotation.JsonValue;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.Serializable;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * ConnectorJobOutput
 * <p>
 * connector command job output
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "outputType",
    "checkConnection",
    "discoverCatalogId",
    "spec",
    "connectorConfigurationUpdated",
    "failureReason"
})
public class ConnectorJobOutput implements Serializable
{

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("outputType")
    private OutputType outputType;
    /**
     * StandardCheckConnectionOutput
     * <p>
     * describes the result of a 'check connection' action.
     * 
     */
    @JsonProperty("checkConnection")
    @JsonPropertyDescription("describes the result of a 'check connection' action.")
    private StandardCheckConnectionOutput checkConnection;
    /**
     * A UUID for the discovered catalog which is persisted by the job
     * 
     */
    @JsonProperty("discoverCatalogId")
    @JsonPropertyDescription("A UUID for the discovered catalog which is persisted by the job")
    private UUID discoverCatalogId;
    @JsonProperty("spec")
    private ConnectorSpecification spec;
    /**
     * A boolean indicating whether the configuration was updated during the job, e.g. if an AirbyteConfigControlMessage was received.
     * 
     */
    @JsonProperty("connectorConfigurationUpdated")
    @JsonPropertyDescription("A boolean indicating whether the configuration was updated during the job, e.g. if an AirbyteConfigControlMessage was received.")
    private Boolean connectorConfigurationUpdated = false;
    /**
     * FailureSummary
     * <p>
     * 
     * 
     */
    @JsonProperty("failureReason")
    private FailureReason failureReason;
    @JsonIgnore
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();
    private final static long serialVersionUID = -9009391856376536265L;

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("outputType")
    public OutputType getOutputType() {
        return outputType;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("outputType")
    public void setOutputType(OutputType outputType) {
        this.outputType = outputType;
    }

    public ConnectorJobOutput withOutputType(OutputType outputType) {
        this.outputType = outputType;
        return this;
    }

    /**
     * StandardCheckConnectionOutput
     * <p>
     * describes the result of a 'check connection' action.
     * 
     */
    @JsonProperty("checkConnection")
    public StandardCheckConnectionOutput getCheckConnection() {
        return checkConnection;
    }

    /**
     * StandardCheckConnectionOutput
     * <p>
     * describes the result of a 'check connection' action.
     * 
     */
    @JsonProperty("checkConnection")
    public void setCheckConnection(StandardCheckConnectionOutput checkConnection) {
        this.checkConnection = checkConnection;
    }

    public ConnectorJobOutput withCheckConnection(StandardCheckConnectionOutput checkConnection) {
        this.checkConnection = checkConnection;
        return this;
    }

    /**
     * A UUID for the discovered catalog which is persisted by the job
     * 
     */
    @JsonProperty("discoverCatalogId")
    public UUID getDiscoverCatalogId() {
        return discoverCatalogId;
    }

    /**
     * A UUID for the discovered catalog which is persisted by the job
     * 
     */
    @JsonProperty("discoverCatalogId")
    public void setDiscoverCatalogId(UUID discoverCatalogId) {
        this.discoverCatalogId = discoverCatalogId;
    }

    public ConnectorJobOutput withDiscoverCatalogId(UUID discoverCatalogId) {
        this.discoverCatalogId = discoverCatalogId;
        return this;
    }

    @JsonProperty("spec")
    public ConnectorSpecification getSpec() {
        return spec;
    }

    @JsonProperty("spec")
    public void setSpec(ConnectorSpecification spec) {
        this.spec = spec;
    }

    public ConnectorJobOutput withSpec(ConnectorSpecification spec) {
        this.spec = spec;
        return this;
    }

    /**
     * A boolean indicating whether the configuration was updated during the job, e.g. if an AirbyteConfigControlMessage was received.
     * 
     */
    @JsonProperty("connectorConfigurationUpdated")
    public Boolean getConnectorConfigurationUpdated() {
        return connectorConfigurationUpdated;
    }

    /**
     * A boolean indicating whether the configuration was updated during the job, e.g. if an AirbyteConfigControlMessage was received.
     * 
     */
    @JsonProperty("connectorConfigurationUpdated")
    public void setConnectorConfigurationUpdated(Boolean connectorConfigurationUpdated) {
        this.connectorConfigurationUpdated = connectorConfigurationUpdated;
    }

    public ConnectorJobOutput withConnectorConfigurationUpdated(Boolean connectorConfigurationUpdated) {
        this.connectorConfigurationUpdated = connectorConfigurationUpdated;
        return this;
    }

    /**
     * FailureSummary
     * <p>
     * 
     * 
     */
    @JsonProperty("failureReason")
    public FailureReason getFailureReason() {
        return failureReason;
    }

    /**
     * FailureSummary
     * <p>
     * 
     * 
     */
    @JsonProperty("failureReason")
    public void setFailureReason(FailureReason failureReason) {
        this.failureReason = failureReason;
    }

    public ConnectorJobOutput withFailureReason(FailureReason failureReason) {
        this.failureReason = failureReason;
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

    public ConnectorJobOutput withAdditionalProperty(String name, Object value) {
        this.additionalProperties.put(name, value);
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(ConnectorJobOutput.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("outputType");
        sb.append('=');
        sb.append(((this.outputType == null)?"<null>":this.outputType));
        sb.append(',');
        sb.append("checkConnection");
        sb.append('=');
        sb.append(((this.checkConnection == null)?"<null>":this.checkConnection));
        sb.append(',');
        sb.append("discoverCatalogId");
        sb.append('=');
        sb.append(((this.discoverCatalogId == null)?"<null>":this.discoverCatalogId));
        sb.append(',');
        sb.append("spec");
        sb.append('=');
        sb.append(((this.spec == null)?"<null>":this.spec));
        sb.append(',');
        sb.append("connectorConfigurationUpdated");
        sb.append('=');
        sb.append(((this.connectorConfigurationUpdated == null)?"<null>":this.connectorConfigurationUpdated));
        sb.append(',');
        sb.append("failureReason");
        sb.append('=');
        sb.append(((this.failureReason == null)?"<null>":this.failureReason));
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
        result = ((result* 31)+((this.checkConnection == null)? 0 :this.checkConnection.hashCode()));
        result = ((result* 31)+((this.connectorConfigurationUpdated == null)? 0 :this.connectorConfigurationUpdated.hashCode()));
        result = ((result* 31)+((this.discoverCatalogId == null)? 0 :this.discoverCatalogId.hashCode()));
        result = ((result* 31)+((this.failureReason == null)? 0 :this.failureReason.hashCode()));
        result = ((result* 31)+((this.outputType == null)? 0 :this.outputType.hashCode()));
        result = ((result* 31)+((this.additionalProperties == null)? 0 :this.additionalProperties.hashCode()));
        result = ((result* 31)+((this.spec == null)? 0 :this.spec.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof ConnectorJobOutput) == false) {
            return false;
        }
        ConnectorJobOutput rhs = ((ConnectorJobOutput) other);
        return ((((((((this.checkConnection == rhs.checkConnection)||((this.checkConnection!= null)&&this.checkConnection.equals(rhs.checkConnection)))&&((this.connectorConfigurationUpdated == rhs.connectorConfigurationUpdated)||((this.connectorConfigurationUpdated!= null)&&this.connectorConfigurationUpdated.equals(rhs.connectorConfigurationUpdated))))&&((this.discoverCatalogId == rhs.discoverCatalogId)||((this.discoverCatalogId!= null)&&this.discoverCatalogId.equals(rhs.discoverCatalogId))))&&((this.failureReason == rhs.failureReason)||((this.failureReason!= null)&&this.failureReason.equals(rhs.failureReason))))&&((this.outputType == rhs.outputType)||((this.outputType!= null)&&this.outputType.equals(rhs.outputType))))&&((this.additionalProperties == rhs.additionalProperties)||((this.additionalProperties!= null)&&this.additionalProperties.equals(rhs.additionalProperties))))&&((this.spec == rhs.spec)||((this.spec!= null)&&this.spec.equals(rhs.spec))));
    }

    public enum OutputType {

        CHECK_CONNECTION("checkConnection"),
        DISCOVER_CATALOG_ID("discoverCatalogId"),
        SPEC("spec");
        private final String value;
        private final static Map<String, OutputType> CONSTANTS = new HashMap<String, OutputType>();

        static {
            for (OutputType c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        private OutputType(String value) {
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
        public static OutputType fromValue(String value) {
            OutputType constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

}
