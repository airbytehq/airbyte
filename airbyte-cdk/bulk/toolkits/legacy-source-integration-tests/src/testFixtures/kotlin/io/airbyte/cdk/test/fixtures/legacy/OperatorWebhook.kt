package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.*
import java.io.Serializable
import java.util.*

/**
 * OperatorWebhook
 *
 *
 * Settings for a webhook operation
 *
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder(
    "executionUrl", "executionBody", "webhookConfigId"
)
class OperatorWebhook : Serializable {
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
    @get:JsonProperty("executionUrl")
    @set:JsonProperty("executionUrl")
    @JsonProperty("executionUrl")
    var executionUrl: String? = null

    @get:JsonProperty("executionBody")
    @set:JsonProperty("executionBody")
    @JsonProperty("executionBody")
    var executionBody: String? = null

    @get:JsonProperty("webhookConfigId")
    @set:JsonProperty("webhookConfigId")
    @JsonProperty("webhookConfigId")
    var webhookConfigId: UUID? = null

    @JsonIgnore
    private val additionalProperties: MutableMap<String, Any>? = HashMap()

    fun withExecutionUrl(executionUrl: String?): OperatorWebhook {
        this.executionUrl = executionUrl
        return this
    }

    fun withExecutionBody(executionBody: String?): OperatorWebhook {
        this.executionBody = executionBody
        return this
    }

    fun withWebhookConfigId(webhookConfigId: UUID?): OperatorWebhook {
        this.webhookConfigId = webhookConfigId
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

    fun withAdditionalProperty(name: String, value: Any): OperatorWebhook {
        additionalProperties!![name] = value
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(OperatorWebhook::class.java.name).append('@').append(
            Integer.toHexString(
                System.identityHashCode(
                    this
                )
            )
        ).append('[')
        sb.append("executionUrl")
        sb.append('=')
        sb.append((if ((this.executionUrl == null)) "<null>" else this.executionUrl))
        sb.append(',')
        sb.append("executionBody")
        sb.append('=')
        sb.append((if ((this.executionBody == null)) "<null>" else this.executionBody))
        sb.append(',')
        sb.append("webhookConfigId")
        sb.append('=')
        sb.append((if ((this.webhookConfigId == null)) "<null>" else this.webhookConfigId))
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
        result = ((result * 31) + (if ((this.webhookConfigId == null)) 0 else webhookConfigId.hashCode()))
        result = ((result * 31) + (if ((this.additionalProperties == null)) 0 else additionalProperties.hashCode()))
        result = ((result * 31) + (if ((this.executionUrl == null)) 0 else executionUrl.hashCode()))
        result = ((result * 31) + (if ((this.executionBody == null)) 0 else executionBody.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is OperatorWebhook) == false) {
            return false
        }
        val rhs = other
        return (((((this.webhookConfigId === rhs.webhookConfigId) || ((this.webhookConfigId != null) && (this.webhookConfigId == rhs.webhookConfigId))) && ((this.additionalProperties === rhs.additionalProperties) || ((this.additionalProperties != null) && (this.additionalProperties == rhs.additionalProperties)))) && ((this.executionUrl === rhs.executionUrl) || ((this.executionUrl != null) && (this.executionUrl == rhs.executionUrl)))) && ((this.executionBody === rhs.executionBody) || ((this.executionBody != null) && (this.executionBody == rhs.executionBody))))
    }

    companion object {
        private const val serialVersionUID = 6156722361495187053L
    }
}
