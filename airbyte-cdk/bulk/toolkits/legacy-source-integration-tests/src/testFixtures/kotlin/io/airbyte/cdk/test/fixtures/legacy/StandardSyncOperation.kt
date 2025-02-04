/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.*
import java.io.Serializable
import java.util.*

/**
 * StandardSyncOperation
 *
 * Configuration of an operation to apply during a sync
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder(
    "operationId",
    "name",
    "operatorType",
    "operatorNormalization",
    "operatorDbt",
    "operatorWebhook",
    "tombstone",
    "workspaceId"
)
class StandardSyncOperation : Serializable {
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
    @get:JsonProperty("operationId")
    @set:JsonProperty("operationId")
    @JsonProperty("operationId")
    var operationId: UUID? = null
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
    @get:JsonProperty("name")
    @set:JsonProperty("name")
    @JsonProperty("name")
    var name: String? = null
    /**
     * OperatorType
     *
     * Type of Operator (Required)
     */
    /**
     * OperatorType
     *
     * Type of Operator (Required)
     */
    /**
     * OperatorType
     *
     * Type of Operator (Required)
     */
    @get:JsonProperty("operatorType")
    @set:JsonProperty("operatorType")
    @JsonProperty("operatorType")
    @JsonPropertyDescription("Type of Operator")
    var operatorType: OperatorType? = null
    /**
     * OperatorNormalization
     *
     * Settings for a normalization operator
     */
    /**
     * OperatorNormalization
     *
     * Settings for a normalization operator
     */
    /**
     * OperatorNormalization
     *
     * Settings for a normalization operator
     */
    @get:JsonProperty("operatorNormalization")
    @set:JsonProperty("operatorNormalization")
    @JsonProperty("operatorNormalization")
    @JsonPropertyDescription("Settings for a normalization operator")
    var operatorNormalization: OperatorNormalization? = null
    /**
     * OperatorDbt
     *
     * Settings for a DBT operator
     */
    /**
     * OperatorDbt
     *
     * Settings for a DBT operator
     */
    /**
     * OperatorDbt
     *
     * Settings for a DBT operator
     */
    @get:JsonProperty("operatorDbt")
    @set:JsonProperty("operatorDbt")
    @JsonProperty("operatorDbt")
    @JsonPropertyDescription("Settings for a DBT operator")
    var operatorDbt: OperatorDbt? = null
    /**
     * OperatorWebhook
     *
     * Settings for a webhook operation
     */
    /**
     * OperatorWebhook
     *
     * Settings for a webhook operation
     */
    /**
     * OperatorWebhook
     *
     * Settings for a webhook operation
     */
    @get:JsonProperty("operatorWebhook")
    @set:JsonProperty("operatorWebhook")
    @JsonProperty("operatorWebhook")
    @JsonPropertyDescription("Settings for a webhook operation")
    var operatorWebhook: OperatorWebhook? = null
    /**
     * if not set or false, the configuration is active. if true, then this configuration is
     * permanently off.
     */
    /**
     * if not set or false, the configuration is active. if true, then this configuration is
     * permanently off.
     */
    /**
     * if not set or false, the configuration is active. if true, then this configuration is
     * permanently off.
     */
    @get:JsonProperty("tombstone")
    @set:JsonProperty("tombstone")
    @JsonProperty("tombstone")
    @JsonPropertyDescription(
        "if not set or false, the configuration is active. if true, then this configuration is permanently off."
    )
    var tombstone: Boolean? = null
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
    @get:JsonProperty("workspaceId")
    @set:JsonProperty("workspaceId")
    @JsonProperty("workspaceId")
    var workspaceId: UUID? = null

    fun withOperationId(operationId: UUID?): StandardSyncOperation {
        this.operationId = operationId
        return this
    }

    fun withName(name: String?): StandardSyncOperation {
        this.name = name
        return this
    }

    fun withOperatorType(operatorType: OperatorType?): StandardSyncOperation {
        this.operatorType = operatorType
        return this
    }

    fun withOperatorNormalization(
        operatorNormalization: OperatorNormalization?
    ): StandardSyncOperation {
        this.operatorNormalization = operatorNormalization
        return this
    }

    fun withOperatorDbt(operatorDbt: OperatorDbt?): StandardSyncOperation {
        this.operatorDbt = operatorDbt
        return this
    }

    fun withOperatorWebhook(operatorWebhook: OperatorWebhook?): StandardSyncOperation {
        this.operatorWebhook = operatorWebhook
        return this
    }

    fun withTombstone(tombstone: Boolean?): StandardSyncOperation {
        this.tombstone = tombstone
        return this
    }

    fun withWorkspaceId(workspaceId: UUID?): StandardSyncOperation {
        this.workspaceId = workspaceId
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(StandardSyncOperation::class.java.name)
            .append('@')
            .append(Integer.toHexString(System.identityHashCode(this)))
            .append('[')
        sb.append("operationId")
        sb.append('=')
        sb.append((if ((this.operationId == null)) "<null>" else this.operationId))
        sb.append(',')
        sb.append("name")
        sb.append('=')
        sb.append((if ((this.name == null)) "<null>" else this.name))
        sb.append(',')
        sb.append("operatorType")
        sb.append('=')
        sb.append((if ((this.operatorType == null)) "<null>" else this.operatorType))
        sb.append(',')
        sb.append("operatorNormalization")
        sb.append('=')
        sb.append(
            (if ((this.operatorNormalization == null)) "<null>" else this.operatorNormalization)
        )
        sb.append(',')
        sb.append("operatorDbt")
        sb.append('=')
        sb.append((if ((this.operatorDbt == null)) "<null>" else this.operatorDbt))
        sb.append(',')
        sb.append("operatorWebhook")
        sb.append('=')
        sb.append((if ((this.operatorWebhook == null)) "<null>" else this.operatorWebhook))
        sb.append(',')
        sb.append("tombstone")
        sb.append('=')
        sb.append((if ((this.tombstone == null)) "<null>" else this.tombstone))
        sb.append(',')
        sb.append("workspaceId")
        sb.append('=')
        sb.append((if ((this.workspaceId == null)) "<null>" else this.workspaceId))
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
        result = ((result * 31) + (if ((this.operatorDbt == null)) 0 else operatorDbt.hashCode()))
        result =
            ((result * 31) +
                (if ((this.operatorWebhook == null)) 0 else operatorWebhook.hashCode()))
        result = ((result * 31) + (if ((this.tombstone == null)) 0 else tombstone.hashCode()))
        result = ((result * 31) + (if ((this.name == null)) 0 else name.hashCode()))
        result = ((result * 31) + (if ((this.operationId == null)) 0 else operationId.hashCode()))
        result =
            ((result * 31) +
                (if ((this.operatorNormalization == null)) 0 else operatorNormalization.hashCode()))
        result = ((result * 31) + (if ((this.operatorType == null)) 0 else operatorType.hashCode()))
        result = ((result * 31) + (if ((this.workspaceId == null)) 0 else workspaceId.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is StandardSyncOperation) == false) {
            return false
        }
        val rhs = other
        return (((((((((this.operatorDbt === rhs.operatorDbt) ||
            ((this.operatorDbt != null) && (this.operatorDbt == rhs.operatorDbt))) &&
            ((this.operatorWebhook === rhs.operatorWebhook) ||
                ((this.operatorWebhook != null) &&
                    (this.operatorWebhook == rhs.operatorWebhook)))) &&
            ((this.tombstone === rhs.tombstone) ||
                ((this.tombstone != null) && (this.tombstone == rhs.tombstone)))) &&
            ((this.name === rhs.name) || ((this.name != null) && (this.name == rhs.name)))) &&
            ((this.operationId === rhs.operationId) ||
                ((this.operationId != null) && (this.operationId == rhs.operationId)))) &&
            ((this.operatorNormalization === rhs.operatorNormalization) ||
                ((this.operatorNormalization != null) &&
                    (this.operatorNormalization == rhs.operatorNormalization)))) &&
            ((this.operatorType == rhs.operatorType) ||
                ((this.operatorType != null) && (this.operatorType == rhs.operatorType)))) &&
            ((this.workspaceId === rhs.workspaceId) ||
                ((this.workspaceId != null) && (this.workspaceId == rhs.workspaceId))))
    }

    /**
     * OperatorType
     *
     * Type of Operator
     */
    enum class OperatorType(private val value: String) {
        NORMALIZATION("normalization"),
        DBT("dbt"),
        WEBHOOK("webhook");

        override fun toString(): String {
            return this.value
        }

        @JsonValue
        fun value(): String {
            return this.value
        }

        companion object {
            private val CONSTANTS: MutableMap<String, OperatorType> = HashMap()

            init {
                for (c in entries) {
                    CONSTANTS[c.value] = c
                }
            }

            @JsonCreator
            fun fromValue(value: String): OperatorType {
                val constant = CONSTANTS[value]
                requireNotNull(constant) { value }
                return constant
            }
        }
    }

    companion object {
        private const val serialVersionUID = 1883842093468364803L
    }
}
