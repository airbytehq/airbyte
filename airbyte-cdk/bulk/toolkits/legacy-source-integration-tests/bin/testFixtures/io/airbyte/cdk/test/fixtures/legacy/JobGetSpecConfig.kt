/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import java.io.Serializable

/**
 * JobGetSpecConfig
 *
 * job check get spec
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder("dockerImage", "isCustomConnector")
class JobGetSpecConfig : Serializable {
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
    @get:JsonProperty("dockerImage")
    @set:JsonProperty("dockerImage")
    @JsonProperty("dockerImage")
    var dockerImage: String? = null
    /** determine if the running image is a custom connector. */
    /** determine if the running image is a custom connector. */
    /** determine if the running image is a custom connector. */
    @get:JsonProperty("isCustomConnector")
    @set:JsonProperty("isCustomConnector")
    @JsonProperty("isCustomConnector")
    @JsonPropertyDescription("determine if the running image is a custom connector.")
    var isCustomConnector: Boolean? = null

    fun withDockerImage(dockerImage: String?): JobGetSpecConfig {
        this.dockerImage = dockerImage
        return this
    }

    fun withIsCustomConnector(isCustomConnector: Boolean?): JobGetSpecConfig {
        this.isCustomConnector = isCustomConnector
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(JobGetSpecConfig::class.java.name)
            .append('@')
            .append(Integer.toHexString(System.identityHashCode(this)))
            .append('[')
        sb.append("dockerImage")
        sb.append('=')
        sb.append((if ((this.dockerImage == null)) "<null>" else this.dockerImage))
        sb.append(',')
        sb.append("isCustomConnector")
        sb.append('=')
        sb.append((if ((this.isCustomConnector == null)) "<null>" else this.isCustomConnector))
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
        result =
            ((result * 31) +
                (if ((this.isCustomConnector == null)) 0 else isCustomConnector.hashCode()))
        result = ((result * 31) + (if ((this.dockerImage == null)) 0 else dockerImage.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is JobGetSpecConfig) == false) {
            return false
        }
        val rhs = other
        return (((this.isCustomConnector === rhs.isCustomConnector) ||
            ((this.isCustomConnector != null) &&
                (this.isCustomConnector == rhs.isCustomConnector))) &&
            ((this.dockerImage === rhs.dockerImage) ||
                ((this.dockerImage != null) && (this.dockerImage == rhs.dockerImage))))
    }

    companion object {
        private const val serialVersionUID = 1959664576657927959L
    }
}
