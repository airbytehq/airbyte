package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import java.io.Serializable

/**
 * ResourceRequirements
 *
 *
 * generic configuration for pod source requirements
 *
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder(
    "cpu_request", "cpu_limit", "memory_request", "memory_limit"
)
class ResourceRequirements : Serializable {
    @get:JsonProperty("cpu_request")
    @set:JsonProperty("cpu_request")
    @JsonProperty("cpu_request")
    var cpuRequest: String? = null

    @get:JsonProperty("cpu_limit")
    @set:JsonProperty("cpu_limit")
    @JsonProperty("cpu_limit")
    var cpuLimit: String? = null

    @get:JsonProperty("memory_request")
    @set:JsonProperty("memory_request")
    @JsonProperty("memory_request")
    var memoryRequest: String? = null

    @get:JsonProperty("memory_limit")
    @set:JsonProperty("memory_limit")
    @JsonProperty("memory_limit")
    var memoryLimit: String? = null

    fun withCpuRequest(cpuRequest: String?): ResourceRequirements {
        this.cpuRequest = cpuRequest
        return this
    }

    fun withCpuLimit(cpuLimit: String?): ResourceRequirements {
        this.cpuLimit = cpuLimit
        return this
    }

    fun withMemoryRequest(memoryRequest: String?): ResourceRequirements {
        this.memoryRequest = memoryRequest
        return this
    }

    fun withMemoryLimit(memoryLimit: String?): ResourceRequirements {
        this.memoryLimit = memoryLimit
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(ResourceRequirements::class.java.name).append('@').append(
            Integer.toHexString(
                System.identityHashCode(
                    this
                )
            )
        ).append('[')
        sb.append("cpuRequest")
        sb.append('=')
        sb.append((if ((this.cpuRequest == null)) "<null>" else this.cpuRequest))
        sb.append(',')
        sb.append("cpuLimit")
        sb.append('=')
        sb.append((if ((this.cpuLimit == null)) "<null>" else this.cpuLimit))
        sb.append(',')
        sb.append("memoryRequest")
        sb.append('=')
        sb.append((if ((this.memoryRequest == null)) "<null>" else this.memoryRequest))
        sb.append(',')
        sb.append("memoryLimit")
        sb.append('=')
        sb.append((if ((this.memoryLimit == null)) "<null>" else this.memoryLimit))
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
        result = ((result * 31) + (if ((this.memoryRequest == null)) 0 else memoryRequest.hashCode()))
        result = ((result * 31) + (if ((this.memoryLimit == null)) 0 else memoryLimit.hashCode()))
        result = ((result * 31) + (if ((this.cpuLimit == null)) 0 else cpuLimit.hashCode()))
        result = ((result * 31) + (if ((this.cpuRequest == null)) 0 else cpuRequest.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is ResourceRequirements) == false) {
            return false
        }
        val rhs = other
        return (((((this.memoryRequest === rhs.memoryRequest) || ((this.memoryRequest != null) && (this.memoryRequest == rhs.memoryRequest))) && ((this.memoryLimit === rhs.memoryLimit) || ((this.memoryLimit != null) && (this.memoryLimit == rhs.memoryLimit)))) && ((this.cpuLimit === rhs.cpuLimit) || ((this.cpuLimit != null) && (this.cpuLimit == rhs.cpuLimit)))) && ((this.cpuRequest === rhs.cpuRequest) || ((this.cpuRequest != null) && (this.cpuRequest == rhs.cpuRequest))))
    }

    companion object {
        private const val serialVersionUID = 4560234143748688189L
    }
}
