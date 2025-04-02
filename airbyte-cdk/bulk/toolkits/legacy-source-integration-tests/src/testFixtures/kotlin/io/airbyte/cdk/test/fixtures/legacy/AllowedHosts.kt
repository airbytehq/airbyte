/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.*
import java.io.Serializable

/**
 * AllowedHosts
 *
 * A connector's allowed hosts. If present, the platform will limit communication to only hosts
 * which are listed in `AllowedHosts.hosts`.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder("hosts")
class AllowedHosts : Serializable {
    /**
     * An array of hosts that this connector can connect to. AllowedHosts not being present for the
     * source or destination means that access to all hosts is allowed. An empty list here means
     * that no network access is granted.
     */
    /**
     * An array of hosts that this connector can connect to. AllowedHosts not being present for the
     * source or destination means that access to all hosts is allowed. An empty list here means
     * that no network access is granted.
     */
    /**
     * An array of hosts that this connector can connect to. AllowedHosts not being present for the
     * source or destination means that access to all hosts is allowed. An empty list here means
     * that no network access is granted.
     */
    @get:JsonProperty("hosts")
    @set:JsonProperty("hosts")
    @JsonProperty("hosts")
    @JsonPropertyDescription(
        "An array of hosts that this connector can connect to.  AllowedHosts not being present for the source or destination means that access to all hosts is allowed.  An empty list here means that no network access is granted."
    )
    var hosts: List<String>? = ArrayList()

    @JsonIgnore private val additionalProperties: MutableMap<String, Any>? = HashMap()

    fun withHosts(hosts: List<String>?): AllowedHosts {
        this.hosts = hosts
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

    fun withAdditionalProperty(name: String, value: Any): AllowedHosts {
        additionalProperties!![name] = value
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(AllowedHosts::class.java.name)
            .append('@')
            .append(Integer.toHexString(System.identityHashCode(this)))
            .append('[')
        sb.append("hosts")
        sb.append('=')
        sb.append((if ((this.hosts == null)) "<null>" else this.hosts))
        sb.append(',')
        sb.append("additionalProperties")
        sb.append('=')
        sb.append(
            (if ((this.additionalProperties == null)) "<null>" else this.additionalProperties)
        )
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
        result = ((result * 31) + (if ((this.hosts == null)) 0 else hosts.hashCode()))
        result =
            ((result * 31) +
                (if ((this.additionalProperties == null)) 0 else additionalProperties.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is AllowedHosts) == false) {
            return false
        }
        val rhs = other
        return (((this.hosts === rhs.hosts) ||
            ((this.hosts != null) && (this.hosts == rhs.hosts))) &&
            ((this.additionalProperties === rhs.additionalProperties) ||
                ((this.additionalProperties != null) &&
                    (this.additionalProperties == rhs.additionalProperties))))
    }

    companion object {
        private const val serialVersionUID = -5046656680170512501L
    }
}
