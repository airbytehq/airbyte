
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

/**
 * FailureSummary
 * <p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "failureOrigin",
    "failureType",
    "internalMessage",
    "externalMessage",
    "metadata",
    "stacktrace",
    "retryable",
    "timestamp"
})
public class FailureReason implements Serializable
{

    /**
     * Indicates where the error originated. If not set, the origin of error is not well known.
     * 
     */
    @JsonProperty("failureOrigin")
    @JsonPropertyDescription("Indicates where the error originated. If not set, the origin of error is not well known.")
    private FailureOrigin failureOrigin;
    /**
     * Categorizes well known errors into types for programmatic handling. If not set, the type of error is not well known.
     * 
     */
    @JsonProperty("failureType")
    @JsonPropertyDescription("Categorizes well known errors into types for programmatic handling. If not set, the type of error is not well known.")
    private FailureType failureType;
    /**
     * Human readable failure description for consumption by technical system operators, like Airbyte engineers or OSS users.
     * 
     */
    @JsonProperty("internalMessage")
    @JsonPropertyDescription("Human readable failure description for consumption by technical system operators, like Airbyte engineers or OSS users.")
    private String internalMessage;
    /**
     * Human readable failure description for presentation in the UI to non-technical users.
     * 
     */
    @JsonProperty("externalMessage")
    @JsonPropertyDescription("Human readable failure description for presentation in the UI to non-technical users.")
    private String externalMessage;
    /**
     * Key-value pairs of relevant data
     * 
     */
    @JsonProperty("metadata")
    @JsonPropertyDescription("Key-value pairs of relevant data")
    private Metadata metadata;
    /**
     * Raw stacktrace associated with the failure.
     * 
     */
    @JsonProperty("stacktrace")
    @JsonPropertyDescription("Raw stacktrace associated with the failure.")
    private String stacktrace;
    /**
     * True if it is known that retrying may succeed, e.g. for a transient failure. False if it is known that a retry will not succeed, e.g. for a configuration issue. If not set, retryable status is not well known.
     * 
     */
    @JsonProperty("retryable")
    @JsonPropertyDescription("True if it is known that retrying may succeed, e.g. for a transient failure. False if it is known that a retry will not succeed, e.g. for a configuration issue. If not set, retryable status is not well known.")
    private Boolean retryable;
    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    private Long timestamp;
    private final static long serialVersionUID = 6398894595031049582L;

    /**
     * Indicates where the error originated. If not set, the origin of error is not well known.
     * 
     */
    @JsonProperty("failureOrigin")
    public FailureOrigin getFailureOrigin() {
        return failureOrigin;
    }

    /**
     * Indicates where the error originated. If not set, the origin of error is not well known.
     * 
     */
    @JsonProperty("failureOrigin")
    public void setFailureOrigin(FailureOrigin failureOrigin) {
        this.failureOrigin = failureOrigin;
    }

    public FailureReason withFailureOrigin(FailureOrigin failureOrigin) {
        this.failureOrigin = failureOrigin;
        return this;
    }

    /**
     * Categorizes well known errors into types for programmatic handling. If not set, the type of error is not well known.
     * 
     */
    @JsonProperty("failureType")
    public FailureType getFailureType() {
        return failureType;
    }

    /**
     * Categorizes well known errors into types for programmatic handling. If not set, the type of error is not well known.
     * 
     */
    @JsonProperty("failureType")
    public void setFailureType(FailureType failureType) {
        this.failureType = failureType;
    }

    public FailureReason withFailureType(FailureType failureType) {
        this.failureType = failureType;
        return this;
    }

    /**
     * Human readable failure description for consumption by technical system operators, like Airbyte engineers or OSS users.
     * 
     */
    @JsonProperty("internalMessage")
    public String getInternalMessage() {
        return internalMessage;
    }

    /**
     * Human readable failure description for consumption by technical system operators, like Airbyte engineers or OSS users.
     * 
     */
    @JsonProperty("internalMessage")
    public void setInternalMessage(String internalMessage) {
        this.internalMessage = internalMessage;
    }

    public FailureReason withInternalMessage(String internalMessage) {
        this.internalMessage = internalMessage;
        return this;
    }

    /**
     * Human readable failure description for presentation in the UI to non-technical users.
     * 
     */
    @JsonProperty("externalMessage")
    public String getExternalMessage() {
        return externalMessage;
    }

    /**
     * Human readable failure description for presentation in the UI to non-technical users.
     * 
     */
    @JsonProperty("externalMessage")
    public void setExternalMessage(String externalMessage) {
        this.externalMessage = externalMessage;
    }

    public FailureReason withExternalMessage(String externalMessage) {
        this.externalMessage = externalMessage;
        return this;
    }

    /**
     * Key-value pairs of relevant data
     * 
     */
    @JsonProperty("metadata")
    public Metadata getMetadata() {
        return metadata;
    }

    /**
     * Key-value pairs of relevant data
     * 
     */
    @JsonProperty("metadata")
    public void setMetadata(Metadata metadata) {
        this.metadata = metadata;
    }

    public FailureReason withMetadata(Metadata metadata) {
        this.metadata = metadata;
        return this;
    }

    /**
     * Raw stacktrace associated with the failure.
     * 
     */
    @JsonProperty("stacktrace")
    public String getStacktrace() {
        return stacktrace;
    }

    /**
     * Raw stacktrace associated with the failure.
     * 
     */
    @JsonProperty("stacktrace")
    public void setStacktrace(String stacktrace) {
        this.stacktrace = stacktrace;
    }

    public FailureReason withStacktrace(String stacktrace) {
        this.stacktrace = stacktrace;
        return this;
    }

    /**
     * True if it is known that retrying may succeed, e.g. for a transient failure. False if it is known that a retry will not succeed, e.g. for a configuration issue. If not set, retryable status is not well known.
     * 
     */
    @JsonProperty("retryable")
    public Boolean getRetryable() {
        return retryable;
    }

    /**
     * True if it is known that retrying may succeed, e.g. for a transient failure. False if it is known that a retry will not succeed, e.g. for a configuration issue. If not set, retryable status is not well known.
     * 
     */
    @JsonProperty("retryable")
    public void setRetryable(Boolean retryable) {
        this.retryable = retryable;
    }

    public FailureReason withRetryable(Boolean retryable) {
        this.retryable = retryable;
        return this;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    public Long getTimestamp() {
        return timestamp;
    }

    /**
     * 
     * (Required)
     * 
     */
    @JsonProperty("timestamp")
    public void setTimestamp(Long timestamp) {
        this.timestamp = timestamp;
    }

    public FailureReason withTimestamp(Long timestamp) {
        this.timestamp = timestamp;
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(FailureReason.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("failureOrigin");
        sb.append('=');
        sb.append(((this.failureOrigin == null)?"<null>":this.failureOrigin));
        sb.append(',');
        sb.append("failureType");
        sb.append('=');
        sb.append(((this.failureType == null)?"<null>":this.failureType));
        sb.append(',');
        sb.append("internalMessage");
        sb.append('=');
        sb.append(((this.internalMessage == null)?"<null>":this.internalMessage));
        sb.append(',');
        sb.append("externalMessage");
        sb.append('=');
        sb.append(((this.externalMessage == null)?"<null>":this.externalMessage));
        sb.append(',');
        sb.append("metadata");
        sb.append('=');
        sb.append(((this.metadata == null)?"<null>":this.metadata));
        sb.append(',');
        sb.append("stacktrace");
        sb.append('=');
        sb.append(((this.stacktrace == null)?"<null>":this.stacktrace));
        sb.append(',');
        sb.append("retryable");
        sb.append('=');
        sb.append(((this.retryable == null)?"<null>":this.retryable));
        sb.append(',');
        sb.append("timestamp");
        sb.append('=');
        sb.append(((this.timestamp == null)?"<null>":this.timestamp));
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
        result = ((result* 31)+((this.retryable == null)? 0 :this.retryable.hashCode()));
        result = ((result* 31)+((this.metadata == null)? 0 :this.metadata.hashCode()));
        result = ((result* 31)+((this.stacktrace == null)? 0 :this.stacktrace.hashCode()));
        result = ((result* 31)+((this.failureOrigin == null)? 0 :this.failureOrigin.hashCode()));
        result = ((result* 31)+((this.failureType == null)? 0 :this.failureType.hashCode()));
        result = ((result* 31)+((this.internalMessage == null)? 0 :this.internalMessage.hashCode()));
        result = ((result* 31)+((this.externalMessage == null)? 0 :this.externalMessage.hashCode()));
        result = ((result* 31)+((this.timestamp == null)? 0 :this.timestamp.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof FailureReason) == false) {
            return false;
        }
        FailureReason rhs = ((FailureReason) other);
        return (((((((((this.retryable == rhs.retryable)||((this.retryable!= null)&&this.retryable.equals(rhs.retryable)))&&((this.metadata == rhs.metadata)||((this.metadata!= null)&&this.metadata.equals(rhs.metadata))))&&((this.stacktrace == rhs.stacktrace)||((this.stacktrace!= null)&&this.stacktrace.equals(rhs.stacktrace))))&&((this.failureOrigin == rhs.failureOrigin)||((this.failureOrigin!= null)&&this.failureOrigin.equals(rhs.failureOrigin))))&&((this.failureType == rhs.failureType)||((this.failureType!= null)&&this.failureType.equals(rhs.failureType))))&&((this.internalMessage == rhs.internalMessage)||((this.internalMessage!= null)&&this.internalMessage.equals(rhs.internalMessage))))&&((this.externalMessage == rhs.externalMessage)||((this.externalMessage!= null)&&this.externalMessage.equals(rhs.externalMessage))))&&((this.timestamp == rhs.timestamp)||((this.timestamp!= null)&&this.timestamp.equals(rhs.timestamp))));
    }


    /**
     * Indicates where the error originated. If not set, the origin of error is not well known.
     * 
     */
    public enum FailureOrigin {

        SOURCE("source"),
        DESTINATION("destination"),
        REPLICATION("replication"),
        PERSISTENCE("persistence"),
        NORMALIZATION("normalization"),
        DBT("dbt"),
        AIRBYTE_PLATFORM("airbyte_platform"),
        UNKNOWN("unknown");
        private final String value;
        private final static Map<String, FailureOrigin> CONSTANTS = new HashMap<String, FailureOrigin>();

        static {
            for (FailureOrigin c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        private FailureOrigin(String value) {
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
        public static FailureOrigin fromValue(String value) {
            FailureOrigin constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }


    /**
     * Categorizes well known errors into types for programmatic handling. If not set, the type of error is not well known.
     * 
     */
    public enum FailureType {

        CONFIG_ERROR("config_error"),
        SYSTEM_ERROR("system_error"),
        MANUAL_CANCELLATION("manual_cancellation"),
        REFRESH_SCHEMA("refresh_schema");
        private final String value;
        private final static Map<String, FailureType> CONSTANTS = new HashMap<String, FailureType>();

        static {
            for (FailureType c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        private FailureType(String value) {
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
        public static FailureType fromValue(String value) {
            FailureType constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

}
