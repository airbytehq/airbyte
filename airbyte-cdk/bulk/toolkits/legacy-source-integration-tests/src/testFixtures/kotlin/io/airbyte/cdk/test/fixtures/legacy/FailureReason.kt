/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.*
import java.io.Serializable

/** FailureSummary */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder(
    "failureOrigin",
    "failureType",
    "internalMessage",
    "externalMessage",
    "metadata",
    "stacktrace",
    "retryable",
    "timestamp"
)
class FailureReason : Serializable {
    /** Indicates where the error originated. If not set, the origin of error is not well known. */
    /** Indicates where the error originated. If not set, the origin of error is not well known. */
    /** Indicates where the error originated. If not set, the origin of error is not well known. */
    @get:JsonProperty("failureOrigin")
    @set:JsonProperty("failureOrigin")
    @JsonProperty("failureOrigin")
    @JsonPropertyDescription(
        "Indicates where the error originated. If not set, the origin of error is not well known."
    )
    var failureOrigin: FailureOrigin? = null
    /**
     * Categorizes well known errors into types for programmatic handling. If not set, the type of
     * error is not well known.
     */
    /**
     * Categorizes well known errors into types for programmatic handling. If not set, the type of
     * error is not well known.
     */
    /**
     * Categorizes well known errors into types for programmatic handling. If not set, the type of
     * error is not well known.
     */
    @get:JsonProperty("failureType")
    @set:JsonProperty("failureType")
    @JsonProperty("failureType")
    @JsonPropertyDescription(
        "Categorizes well known errors into types for programmatic handling. If not set, the type of error is not well known."
    )
    var failureType: FailureType? = null
    /**
     * Human readable failure description for consumption by technical system operators, like
     * Airbyte engineers or OSS users.
     */
    /**
     * Human readable failure description for consumption by technical system operators, like
     * Airbyte engineers or OSS users.
     */
    /**
     * Human readable failure description for consumption by technical system operators, like
     * Airbyte engineers or OSS users.
     */
    @get:JsonProperty("internalMessage")
    @set:JsonProperty("internalMessage")
    @JsonProperty("internalMessage")
    @JsonPropertyDescription(
        "Human readable failure description for consumption by technical system operators, like Airbyte engineers or OSS users."
    )
    var internalMessage: String? = null
    /** Human readable failure description for presentation in the UI to non-technical users. */
    /** Human readable failure description for presentation in the UI to non-technical users. */
    /** Human readable failure description for presentation in the UI to non-technical users. */
    @get:JsonProperty("externalMessage")
    @set:JsonProperty("externalMessage")
    @JsonProperty("externalMessage")
    @JsonPropertyDescription(
        "Human readable failure description for presentation in the UI to non-technical users."
    )
    var externalMessage: String? = null
    /** Key-value pairs of relevant data */
    /** Key-value pairs of relevant data */
    /** Key-value pairs of relevant data */
    @get:JsonProperty("metadata")
    @set:JsonProperty("metadata")
    @JsonProperty("metadata")
    @JsonPropertyDescription("Key-value pairs of relevant data")
    var metadata: Metadata? = null
    /** Raw stacktrace associated with the failure. */
    /** Raw stacktrace associated with the failure. */
    /** Raw stacktrace associated with the failure. */
    @get:JsonProperty("stacktrace")
    @set:JsonProperty("stacktrace")
    @JsonProperty("stacktrace")
    @JsonPropertyDescription("Raw stacktrace associated with the failure.")
    var stacktrace: String? = null
    /**
     * True if it is known that retrying may succeed, e.g. for a transient failure. False if it is
     * known that a retry will not succeed, e.g. for a configuration issue. If not set, retryable
     * status is not well known.
     */
    /**
     * True if it is known that retrying may succeed, e.g. for a transient failure. False if it is
     * known that a retry will not succeed, e.g. for a configuration issue. If not set, retryable
     * status is not well known.
     */
    /**
     * True if it is known that retrying may succeed, e.g. for a transient failure. False if it is
     * known that a retry will not succeed, e.g. for a configuration issue. If not set, retryable
     * status is not well known.
     */
    @get:JsonProperty("retryable")
    @set:JsonProperty("retryable")
    @JsonProperty("retryable")
    @JsonPropertyDescription(
        "True if it is known that retrying may succeed, e.g. for a transient failure. False if it is known that a retry will not succeed, e.g. for a configuration issue. If not set, retryable status is not well known."
    )
    var retryable: Boolean? = null
    /**
     *
     * (Required)
     */
    /**
     *
     * (Required)
     */
    /**
     *
     * (Required)
     */
    @get:JsonProperty("timestamp")
    @set:JsonProperty("timestamp")
    @JsonProperty("timestamp")
    var timestamp: Long? = null

    fun withFailureOrigin(failureOrigin: FailureOrigin?): FailureReason {
        this.failureOrigin = failureOrigin
        return this
    }

    fun withFailureType(failureType: FailureType?): FailureReason {
        this.failureType = failureType
        return this
    }

    fun withInternalMessage(internalMessage: String?): FailureReason {
        this.internalMessage = internalMessage
        return this
    }

    fun withExternalMessage(externalMessage: String?): FailureReason {
        this.externalMessage = externalMessage
        return this
    }

    fun withMetadata(metadata: Metadata?): FailureReason {
        this.metadata = metadata
        return this
    }

    fun withStacktrace(stacktrace: String?): FailureReason {
        this.stacktrace = stacktrace
        return this
    }

    fun withRetryable(retryable: Boolean?): FailureReason {
        this.retryable = retryable
        return this
    }

    fun withTimestamp(timestamp: Long?): FailureReason {
        this.timestamp = timestamp
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(FailureReason::class.java.name)
            .append('@')
            .append(Integer.toHexString(System.identityHashCode(this)))
            .append('[')
        sb.append("failureOrigin")
        sb.append('=')
        sb.append((if ((this.failureOrigin == null)) "<null>" else this.failureOrigin))
        sb.append(',')
        sb.append("failureType")
        sb.append('=')
        sb.append((if ((this.failureType == null)) "<null>" else this.failureType))
        sb.append(',')
        sb.append("internalMessage")
        sb.append('=')
        sb.append((if ((this.internalMessage == null)) "<null>" else this.internalMessage))
        sb.append(',')
        sb.append("externalMessage")
        sb.append('=')
        sb.append((if ((this.externalMessage == null)) "<null>" else this.externalMessage))
        sb.append(',')
        sb.append("metadata")
        sb.append('=')
        sb.append((if ((this.metadata == null)) "<null>" else this.metadata))
        sb.append(',')
        sb.append("stacktrace")
        sb.append('=')
        sb.append((if ((this.stacktrace == null)) "<null>" else this.stacktrace))
        sb.append(',')
        sb.append("retryable")
        sb.append('=')
        sb.append((if ((this.retryable == null)) "<null>" else this.retryable))
        sb.append(',')
        sb.append("timestamp")
        sb.append('=')
        sb.append((if ((this.timestamp == null)) "<null>" else this.timestamp))
        sb.append(',')
        if (sb[sb.length - 1] == ',') {
            sb.setCharAt((sb.length - 1), ']')
        } else {
            sb.append(']')
        }
        return sb.toString()
    }

    override fun hashCode(): Int {
        var result = 1
        result = ((result * 31) + (if ((this.retryable == null)) 0 else retryable.hashCode()))
        result = ((result * 31) + (if ((this.metadata == null)) 0 else metadata.hashCode()))
        result = ((result * 31) + (if ((this.stacktrace == null)) 0 else stacktrace.hashCode()))
        result =
            ((result * 31) + (if ((this.failureOrigin == null)) 0 else failureOrigin.hashCode()))
        result = ((result * 31) + (if ((this.failureType == null)) 0 else failureType.hashCode()))
        result =
            ((result * 31) +
                (if ((this.internalMessage == null)) 0 else internalMessage.hashCode()))
        result =
            ((result * 31) +
                (if ((this.externalMessage == null)) 0 else externalMessage.hashCode()))
        result = ((result * 31) + (if ((this.timestamp == null)) 0 else timestamp.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is FailureReason) == false) {
            return false
        }
        val rhs = other
        return (((((((((this.retryable === rhs.retryable) ||
            ((this.retryable != null) && (this.retryable == rhs.retryable))) &&
            ((this.metadata === rhs.metadata) ||
                ((this.metadata != null) && metadata!!.equals(rhs.metadata)))) &&
            ((this.stacktrace === rhs.stacktrace) ||
                ((this.stacktrace != null) && (this.stacktrace == rhs.stacktrace)))) &&
            ((this.failureOrigin == rhs.failureOrigin) ||
                ((this.failureOrigin != null) && (this.failureOrigin == rhs.failureOrigin)))) &&
            ((this.failureType == rhs.failureType) ||
                ((this.failureType != null) && (this.failureType == rhs.failureType)))) &&
            ((this.internalMessage === rhs.internalMessage) ||
                ((this.internalMessage != null) &&
                    (this.internalMessage == rhs.internalMessage)))) &&
            ((this.externalMessage === rhs.externalMessage) ||
                ((this.externalMessage != null) &&
                    (this.externalMessage == rhs.externalMessage)))) &&
            ((this.timestamp === rhs.timestamp) ||
                ((this.timestamp != null) && (this.timestamp == rhs.timestamp))))
    }

    /** Indicates where the error originated. If not set, the origin of error is not well known. */
    enum class FailureOrigin(private val value: String) {
        SOURCE("source"),
        DESTINATION("destination"),
        REPLICATION("replication"),
        PERSISTENCE("persistence"),
        NORMALIZATION("normalization"),
        DBT("dbt"),
        AIRBYTE_PLATFORM("airbyte_platform"),
        UNKNOWN("unknown");

        override fun toString(): String {
            return this.value
        }

        @JsonValue
        fun value(): String {
            return this.value
        }

        companion object {
            private val CONSTANTS: MutableMap<String, FailureOrigin> = HashMap()

            init {
                for (c in entries) {
                    CONSTANTS[c.value] = c
                }
            }

            @JsonCreator
            fun fromValue(value: String): FailureOrigin {
                val constant = CONSTANTS[value]
                requireNotNull(constant) { value }
                return constant
            }
        }
    }

    /**
     * Categorizes well known errors into types for programmatic handling. If not set, the type of
     * error is not well known.
     */
    enum class FailureType(private val value: String) {
        CONFIG_ERROR("config_error"),
        SYSTEM_ERROR("system_error"),
        MANUAL_CANCELLATION("manual_cancellation"),
        REFRESH_SCHEMA("refresh_schema");

        override fun toString(): String {
            return this.value
        }

        @JsonValue
        fun value(): String {
            return this.value
        }

        companion object {
            private val CONSTANTS: MutableMap<String, FailureType> = HashMap()

            init {
                for (c in entries) {
                    CONSTANTS[c.value] = c
                }
            }

            @JsonCreator
            fun fromValue(value: String): FailureType {
                val constant = CONSTANTS[value]
                requireNotNull(constant) { value }
                return constant
            }
        }
    }

    companion object {
        private const val serialVersionUID = 6398894595031049582L
    }
}
