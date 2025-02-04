/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.*
import java.io.Serializable

/** Key-value pairs of relevant data */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder
class Metadata : Serializable {
    @JsonIgnore
    val additionalProperties: MutableMap<String, Any?> = HashMap()
        @JsonAnyGetter get

    @JsonAnySetter
    fun setAdditionalProperty(name: String, value: Any) {
        additionalProperties[name] = value
    }

    fun withAdditionalProperty(name: String, value: Any?): Metadata {
        additionalProperties[name] = value
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(Metadata::class.java.name)
            .append('@')
            .append(Integer.toHexString(System.identityHashCode(this)))
            .append('[')
        sb.append("additionalProperties")
        sb.append('=')
        sb.append(this.additionalProperties)
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
        result = ((result * 31) + (additionalProperties.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if (!(other is Metadata)) {
            return false
        }
        val rhs = other
        return ((this.additionalProperties === rhs.additionalProperties) ||
            (this.additionalProperties == rhs.additionalProperties))
    }

    companion object {
        private const val serialVersionUID = 1605654113251455503L
        /** General Metadata */
        const val JOB_LABEL_KEY: String = "job_id"
        const val ATTEMPT_LABEL_KEY: String = "attempt_id"
        const val WORKER_POD_LABEL_KEY: String = "airbyte"
        const val WORKER_POD_LABEL_VALUE: String = "job-pod"
        const val CONNECTION_ID_LABEL_KEY: String = "connection_id"

        /** These are more readable forms of [io.airbyte.config.JobTypeResourceLimit.JobType]. */
        const val JOB_TYPE_KEY: String = "job_type"
        const val SYNC_JOB: String = "sync"
        const val SPEC_JOB: String = "spec"
        const val CHECK_JOB: String = "check"
        const val DISCOVER_JOB: String = "discover"

        /**
         * A sync job can actually be broken down into the following steps. Try to be as precise as
         * possible with naming/labels to help operations.
         */
        const val SYNC_STEP_KEY: String = "sync_step"
        const val READ_STEP: String = "read"
        const val WRITE_STEP: String = "write"
        const val NORMALIZE_STEP: String = "normalize"
        const val CUSTOM_STEP: String = "custom"
        const val ORCHESTRATOR_STEP: String = "orchestrator"
    }
}
