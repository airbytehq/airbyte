package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.*
import io.airbyte.protocol.models.ConnectorSpecification
import java.io.Serializable
import java.util.*

/**
 * ConnectorJobOutput
 *
 *
 * connector command job output
 *
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder(
    "outputType", "checkConnection", "discoverCatalogId", "spec", "connectorConfigurationUpdated", "failureReason"
)
class ConnectorJobOutput : Serializable {
    /**
     *
     * (Required)
     *
     */
    /**
     *
     * (Required)
     *
     */
    /**
     *
     * (Required)
     *
     */
    @get:JsonProperty("outputType")
    @set:JsonProperty("outputType")
    @JsonProperty("outputType")
    var outputType: OutputType? = null
    /**
     * StandardCheckConnectionOutput
     *
     *
     * describes the result of a 'check connection' action.
     *
     */
    /**
     * StandardCheckConnectionOutput
     *
     *
     * describes the result of a 'check connection' action.
     *
     */
    /**
     * StandardCheckConnectionOutput
     *
     *
     * describes the result of a 'check connection' action.
     *
     */
    @get:JsonProperty("checkConnection")
    @set:JsonProperty("checkConnection")
    @JsonProperty("checkConnection")
    @JsonPropertyDescription("describes the result of a 'check connection' action.")
    var checkConnection: StandardCheckConnectionOutput? = null
    /**
     * A UUID for the discovered catalog which is persisted by the job
     *
     */
    /**
     * A UUID for the discovered catalog which is persisted by the job
     *
     */
    /**
     * A UUID for the discovered catalog which is persisted by the job
     *
     */
    @get:JsonProperty("discoverCatalogId")
    @set:JsonProperty("discoverCatalogId")
    @JsonProperty("discoverCatalogId")
    @JsonPropertyDescription("A UUID for the discovered catalog which is persisted by the job")
    var discoverCatalogId: UUID? = null

    @get:JsonProperty("spec")
    @set:JsonProperty("spec")
    @JsonProperty("spec")
    var spec: ConnectorSpecification? = null
    /**
     * A boolean indicating whether the configuration was updated during the job, e.g. if an AirbyteConfigControlMessage was received.
     *
     */
    /**
     * A boolean indicating whether the configuration was updated during the job, e.g. if an AirbyteConfigControlMessage was received.
     *
     */
    /**
     * A boolean indicating whether the configuration was updated during the job, e.g. if an AirbyteConfigControlMessage was received.
     *
     */
    @get:JsonProperty("connectorConfigurationUpdated")
    @set:JsonProperty("connectorConfigurationUpdated")
    @JsonProperty("connectorConfigurationUpdated")
    @JsonPropertyDescription("A boolean indicating whether the configuration was updated during the job, e.g. if an AirbyteConfigControlMessage was received.")
    var connectorConfigurationUpdated: Boolean? = false
    /**
     * FailureSummary
     *
     *
     *
     *
     */
    /**
     * FailureSummary
     *
     *
     *
     *
     */
    /**
     * FailureSummary
     *
     *
     *
     *
     */
    @get:JsonProperty("failureReason")
    @set:JsonProperty("failureReason")
    @JsonProperty("failureReason")
    var failureReason: FailureReason? = null

    @JsonIgnore
    private val additionalProperties: MutableMap<String, Any>? = HashMap()

    fun withOutputType(outputType: OutputType?): ConnectorJobOutput {
        this.outputType = outputType
        return this
    }

    fun withCheckConnection(checkConnection: StandardCheckConnectionOutput?): ConnectorJobOutput {
        this.checkConnection = checkConnection
        return this
    }

    fun withDiscoverCatalogId(discoverCatalogId: UUID?): ConnectorJobOutput {
        this.discoverCatalogId = discoverCatalogId
        return this
    }

    fun withSpec(spec: ConnectorSpecification?): ConnectorJobOutput {
        this.spec = spec
        return this
    }

    fun withConnectorConfigurationUpdated(connectorConfigurationUpdated: Boolean?): ConnectorJobOutput {
        this.connectorConfigurationUpdated = connectorConfigurationUpdated
        return this
    }

    fun withFailureReason(failureReason: FailureReason?): ConnectorJobOutput {
        this.failureReason = failureReason
        return this
    }

    @JsonAnyGetter
    fun getAdditionalProperties(): Map<String, Any>? {
        return this.additionalProperties
    }

    @JsonAnySetter
    fun setAdditionalProperty(name: String, value: Any) {
        additionalProperties!![name] = value
    }

    fun withAdditionalProperty(name: String, value: Any): ConnectorJobOutput {
        additionalProperties!![name] = value
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(ConnectorJobOutput::class.java.name).append('@').append(
            Integer.toHexString(
                System.identityHashCode(
                    this
                )
            )
        ).append('[')
        sb.append("outputType")
        sb.append('=')
        sb.append((if ((this.outputType == null)) "<null>" else this.outputType))
        sb.append(',')
        sb.append("checkConnection")
        sb.append('=')
        sb.append((if ((this.checkConnection == null)) "<null>" else this.checkConnection))
        sb.append(',')
        sb.append("discoverCatalogId")
        sb.append('=')
        sb.append((if ((this.discoverCatalogId == null)) "<null>" else this.discoverCatalogId))
        sb.append(',')
        sb.append("spec")
        sb.append('=')
        sb.append((if ((this.spec == null)) "<null>" else this.spec))
        sb.append(',')
        sb.append("connectorConfigurationUpdated")
        sb.append('=')
        sb.append((if ((this.connectorConfigurationUpdated == null)) "<null>" else this.connectorConfigurationUpdated))
        sb.append(',')
        sb.append("failureReason")
        sb.append('=')
        sb.append((if ((this.failureReason == null)) "<null>" else this.failureReason))
        sb.append(',')
        sb.append("additionalProperties")
        sb.append('=')
        sb.append((if ((this.additionalProperties == null)) "<null>" else this.additionalProperties))
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
        result = ((result * 31) + (if ((this.checkConnection == null)) 0 else checkConnection.hashCode()))
        result = ((result * 31) + (if ((this.connectorConfigurationUpdated == null)) 0 else connectorConfigurationUpdated.hashCode()))
        result = ((result * 31) + (if ((this.discoverCatalogId == null)) 0 else discoverCatalogId.hashCode()))
        result = ((result * 31) + (if ((this.failureReason == null)) 0 else failureReason.hashCode()))
        result = ((result * 31) + (if ((this.outputType == null)) 0 else outputType.hashCode()))
        result = ((result * 31) + (if ((this.additionalProperties == null)) 0 else additionalProperties.hashCode()))
        result = ((result * 31) + (if ((this.spec == null)) 0 else spec.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is ConnectorJobOutput) == false) {
            return false
        }
        val rhs = other
        return ((((((((this.checkConnection === rhs.checkConnection) || ((this.checkConnection != null) && checkConnection!!.equals(rhs.checkConnection))) && ((this.connectorConfigurationUpdated === rhs.connectorConfigurationUpdated) || ((this.connectorConfigurationUpdated != null) && (this.connectorConfigurationUpdated == rhs.connectorConfigurationUpdated)))) && ((this.discoverCatalogId === rhs.discoverCatalogId) || ((this.discoverCatalogId != null) && (this.discoverCatalogId == rhs.discoverCatalogId)))) && ((this.failureReason === rhs.failureReason) || ((this.failureReason != null) && (this.failureReason == rhs.failureReason)))) && ((this.outputType == rhs.outputType) || ((this.outputType != null) && (this.outputType == rhs.outputType)))) && ((this.additionalProperties === rhs.additionalProperties) || ((this.additionalProperties != null) && (this.additionalProperties == rhs.additionalProperties)))) && ((this.spec === rhs.spec) || ((this.spec != null) && (this.spec == rhs.spec))))
    }

    enum class OutputType(private val value: String) {
        CHECK_CONNECTION("checkConnection"),
        DISCOVER_CATALOG_ID("discoverCatalogId"),
        SPEC("spec");

        override fun toString(): String {
            return this.value
        }

        @JsonValue
        fun value(): String {
            return this.value
        }

        companion object {
            private val CONSTANTS: MutableMap<String, OutputType> = HashMap()

            init {
                for (c in entries) {
                    CONSTANTS[c.value] = c
                }
            }

            @JsonCreator
            fun fromValue(value: String): OutputType {
                val constant = CONSTANTS[value]
                requireNotNull(constant) { value }
                return constant
            }
        }
    }

    companion object {
        private const val serialVersionUID = -9009391856376536265L
    }
}
