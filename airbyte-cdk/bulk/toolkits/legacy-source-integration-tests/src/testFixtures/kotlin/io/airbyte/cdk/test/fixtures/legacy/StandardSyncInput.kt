package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog
import java.io.Serializable
import java.util.*

/**
 * StandardSyncInput
 *
 *
 * job sync config
 *
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder(
    "namespaceDefinition",
    "namespaceFormat",
    "prefix",
    "sourceId",
    "destinationId",
    "sourceConfiguration",
    "destinationConfiguration",
    "operationSequence",
    "webhookOperationConfigs",
    "catalog",
    "state",
    "resourceRequirements",
    "sourceResourceRequirements",
    "destinationResourceRequirements",
    "workspaceId",
    "connectionId"
)
class StandardSyncInput : Serializable {
    /**
     * Namespace Definition
     *
     *
     * Method used for computing final namespace in destination
     *
     */
    /**
     * Namespace Definition
     *
     *
     * Method used for computing final namespace in destination
     *
     */
    /**
     * Namespace Definition
     *
     *
     * Method used for computing final namespace in destination
     *
     */
    @get:JsonProperty("namespaceDefinition")
    @set:JsonProperty("namespaceDefinition")
    @JsonProperty("namespaceDefinition")
    @JsonPropertyDescription("Method used for computing final namespace in destination")
    var namespaceDefinition: JobSyncConfig.NamespaceDefinitionType? = JobSyncConfig.NamespaceDefinitionType.fromValue("source")

    @get:JsonProperty("namespaceFormat")
    @set:JsonProperty("namespaceFormat")
    @JsonProperty("namespaceFormat")
    var namespaceFormat: String? = null
    /**
     * Prefix that will be prepended to the name of each stream when it is written to the destination.
     *
     */
    /**
     * Prefix that will be prepended to the name of each stream when it is written to the destination.
     *
     */
    /**
     * Prefix that will be prepended to the name of each stream when it is written to the destination.
     *
     */
    @get:JsonProperty("prefix")
    @set:JsonProperty("prefix")
    @JsonProperty("prefix")
    @JsonPropertyDescription("Prefix that will be prepended to the name of each stream when it is written to the destination.")
    var prefix: String? = null
    /**
     * Actor ID for the source used in the sync - this is used to update the actor configuration when requested.
     * (Required)
     *
     */
    /**
     * Actor ID for the source used in the sync - this is used to update the actor configuration when requested.
     * (Required)
     *
     */
    /**
     * Actor ID for the source used in the sync - this is used to update the actor configuration when requested.
     * (Required)
     *
     */
    @get:JsonProperty("sourceId")
    @set:JsonProperty("sourceId")
    @JsonProperty("sourceId")
    @JsonPropertyDescription("Actor ID for the source used in the sync - this is used to update the actor configuration when requested.")
    var sourceId: UUID? = null
    /**
     * Actor ID for the destination used in the sync - this is used to update the actor configuration when requested.
     * (Required)
     *
     */
    /**
     * Actor ID for the destination used in the sync - this is used to update the actor configuration when requested.
     * (Required)
     *
     */
    /**
     * Actor ID for the destination used in the sync - this is used to update the actor configuration when requested.
     * (Required)
     *
     */
    @get:JsonProperty("destinationId")
    @set:JsonProperty("destinationId")
    @JsonProperty("destinationId")
    @JsonPropertyDescription("Actor ID for the destination used in the sync - this is used to update the actor configuration when requested.")
    var destinationId: UUID? = null
    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     *
     */
    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     *
     */
    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     *
     */
    @get:JsonProperty("sourceConfiguration")
    @set:JsonProperty("sourceConfiguration")
    @JsonProperty("sourceConfiguration")
    @JsonPropertyDescription("Integration specific blob. Must be a valid JSON string.")
    var sourceConfiguration: JsonNode? = null
    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     *
     */
    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     *
     */
    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     *
     */
    @get:JsonProperty("destinationConfiguration")
    @set:JsonProperty("destinationConfiguration")
    @JsonProperty("destinationConfiguration")
    @JsonPropertyDescription("Integration specific blob. Must be a valid JSON string.")
    var destinationConfiguration: JsonNode? = null
    /**
     * Sequence of configurations of operations to apply as part of the sync
     *
     */
    /**
     * Sequence of configurations of operations to apply as part of the sync
     *
     */
    /**
     * Sequence of configurations of operations to apply as part of the sync
     *
     */
    @get:JsonProperty("operationSequence")
    @set:JsonProperty("operationSequence")
    @JsonProperty("operationSequence")
    @JsonPropertyDescription("Sequence of configurations of operations to apply as part of the sync")
    var operationSequence: List<StandardSyncOperation>? = ArrayList()
    /**
     * The webhook operation configs belonging to this workspace. See webhookOperationConfigs in StandardWorkspace.yaml.
     *
     */
    /**
     * The webhook operation configs belonging to this workspace. See webhookOperationConfigs in StandardWorkspace.yaml.
     *
     */
    /**
     * The webhook operation configs belonging to this workspace. See webhookOperationConfigs in StandardWorkspace.yaml.
     *
     */
    @get:JsonProperty("webhookOperationConfigs")
    @set:JsonProperty("webhookOperationConfigs")
    @JsonProperty("webhookOperationConfigs")
    @JsonPropertyDescription("The webhook operation configs belonging to this workspace. See webhookOperationConfigs in StandardWorkspace.yaml.")
    var webhookOperationConfigs: JsonNode? = null
    /**
     * the configured airbyte catalog
     * (Required)
     *
     */
    /**
     * the configured airbyte catalog
     * (Required)
     *
     */
    /**
     * the configured airbyte catalog
     * (Required)
     *
     */
    @get:JsonProperty("catalog")
    @set:JsonProperty("catalog")
    @JsonProperty("catalog")
    @JsonPropertyDescription("the configured airbyte catalog")
    var catalog: ConfiguredAirbyteCatalog? = null
    /**
     * State
     *
     *
     * information output by the connection.
     *
     */
    /**
     * State
     *
     *
     * information output by the connection.
     *
     */
    /**
     * State
     *
     *
     * information output by the connection.
     *
     */
    @get:JsonProperty("state")
    @set:JsonProperty("state")
    @JsonProperty("state")
    @JsonPropertyDescription("information output by the connection.")
    var state: State? = null
    /**
     * ResourceRequirements
     *
     *
     * generic configuration for pod source requirements
     *
     */
    /**
     * ResourceRequirements
     *
     *
     * generic configuration for pod source requirements
     *
     */
    /**
     * ResourceRequirements
     *
     *
     * generic configuration for pod source requirements
     *
     */
    @get:JsonProperty("resourceRequirements")
    @set:JsonProperty("resourceRequirements")
    @JsonProperty("resourceRequirements")
    @JsonPropertyDescription("generic configuration for pod source requirements")
    var resourceRequirements: ResourceRequirements? = null
    /**
     * ResourceRequirements
     *
     *
     * generic configuration for pod source requirements
     *
     */
    /**
     * ResourceRequirements
     *
     *
     * generic configuration for pod source requirements
     *
     */
    /**
     * ResourceRequirements
     *
     *
     * generic configuration for pod source requirements
     *
     */
    @get:JsonProperty("sourceResourceRequirements")
    @set:JsonProperty("sourceResourceRequirements")
    @JsonProperty("sourceResourceRequirements")
    @JsonPropertyDescription("generic configuration for pod source requirements")
    var sourceResourceRequirements: ResourceRequirements? = null
    /**
     * ResourceRequirements
     *
     *
     * generic configuration for pod source requirements
     *
     */
    /**
     * ResourceRequirements
     *
     *
     * generic configuration for pod source requirements
     *
     */
    /**
     * ResourceRequirements
     *
     *
     * generic configuration for pod source requirements
     *
     */
    @get:JsonProperty("destinationResourceRequirements")
    @set:JsonProperty("destinationResourceRequirements")
    @JsonProperty("destinationResourceRequirements")
    @JsonPropertyDescription("generic configuration for pod source requirements")
    var destinationResourceRequirements: ResourceRequirements? = null
    /**
     * The id of the workspace associated with this sync
     *
     */
    /**
     * The id of the workspace associated with this sync
     *
     */
    /**
     * The id of the workspace associated with this sync
     *
     */
    @get:JsonProperty("workspaceId")
    @set:JsonProperty("workspaceId")
    @JsonProperty("workspaceId")
    @JsonPropertyDescription("The id of the workspace associated with this sync")
    var workspaceId: UUID? = null
    /**
     * The id of the connection associated with this sync
     *
     */
    /**
     * The id of the connection associated with this sync
     *
     */
    /**
     * The id of the connection associated with this sync
     *
     */
    @get:JsonProperty("connectionId")
    @set:JsonProperty("connectionId")
    @JsonProperty("connectionId")
    @JsonPropertyDescription("The id of the connection associated with this sync")
    var connectionId: UUID? = null

    fun withNamespaceDefinition(namespaceDefinition: JobSyncConfig.NamespaceDefinitionType?): StandardSyncInput {
        this.namespaceDefinition = namespaceDefinition
        return this
    }

    fun withNamespaceFormat(namespaceFormat: String?): StandardSyncInput {
        this.namespaceFormat = namespaceFormat
        return this
    }

    fun withPrefix(prefix: String?): StandardSyncInput {
        this.prefix = prefix
        return this
    }

    fun withSourceId(sourceId: UUID?): StandardSyncInput {
        this.sourceId = sourceId
        return this
    }

    fun withDestinationId(destinationId: UUID?): StandardSyncInput {
        this.destinationId = destinationId
        return this
    }

    fun withSourceConfiguration(sourceConfiguration: JsonNode?): StandardSyncInput {
        this.sourceConfiguration = sourceConfiguration
        return this
    }

    fun withDestinationConfiguration(destinationConfiguration: JsonNode?): StandardSyncInput {
        this.destinationConfiguration = destinationConfiguration
        return this
    }

    fun withOperationSequence(operationSequence: List<StandardSyncOperation>?): StandardSyncInput {
        this.operationSequence = operationSequence
        return this
    }

    fun withWebhookOperationConfigs(webhookOperationConfigs: JsonNode?): StandardSyncInput {
        this.webhookOperationConfigs = webhookOperationConfigs
        return this
    }

    fun withCatalog(catalog: ConfiguredAirbyteCatalog?): StandardSyncInput {
        this.catalog = catalog
        return this
    }

    fun withState(state: State?): StandardSyncInput {
        this.state = state
        return this
    }

    fun withResourceRequirements(resourceRequirements: ResourceRequirements?): StandardSyncInput {
        this.resourceRequirements = resourceRequirements
        return this
    }

    fun withSourceResourceRequirements(sourceResourceRequirements: ResourceRequirements?): StandardSyncInput {
        this.sourceResourceRequirements = sourceResourceRequirements
        return this
    }

    fun withDestinationResourceRequirements(destinationResourceRequirements: ResourceRequirements?): StandardSyncInput {
        this.destinationResourceRequirements = destinationResourceRequirements
        return this
    }

    fun withWorkspaceId(workspaceId: UUID?): StandardSyncInput {
        this.workspaceId = workspaceId
        return this
    }

    fun withConnectionId(connectionId: UUID?): StandardSyncInput {
        this.connectionId = connectionId
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(StandardSyncInput::class.java.name).append('@').append(
            Integer.toHexString(
                System.identityHashCode(
                    this
                )
            )
        ).append('[')
        sb.append("namespaceDefinition")
        sb.append('=')
        sb.append((if ((this.namespaceDefinition == null)) "<null>" else this.namespaceDefinition))
        sb.append(',')
        sb.append("namespaceFormat")
        sb.append('=')
        sb.append((if ((this.namespaceFormat == null)) "<null>" else this.namespaceFormat))
        sb.append(',')
        sb.append("prefix")
        sb.append('=')
        sb.append((if ((this.prefix == null)) "<null>" else this.prefix))
        sb.append(',')
        sb.append("sourceId")
        sb.append('=')
        sb.append((if ((this.sourceId == null)) "<null>" else this.sourceId))
        sb.append(',')
        sb.append("destinationId")
        sb.append('=')
        sb.append((if ((this.destinationId == null)) "<null>" else this.destinationId))
        sb.append(',')
        sb.append("sourceConfiguration")
        sb.append('=')
        sb.append((if ((this.sourceConfiguration == null)) "<null>" else this.sourceConfiguration))
        sb.append(',')
        sb.append("destinationConfiguration")
        sb.append('=')
        sb.append((if ((this.destinationConfiguration == null)) "<null>" else this.destinationConfiguration))
        sb.append(',')
        sb.append("operationSequence")
        sb.append('=')
        sb.append((if ((this.operationSequence == null)) "<null>" else this.operationSequence))
        sb.append(',')
        sb.append("webhookOperationConfigs")
        sb.append('=')
        sb.append((if ((this.webhookOperationConfigs == null)) "<null>" else this.webhookOperationConfigs))
        sb.append(',')
        sb.append("catalog")
        sb.append('=')
        sb.append((if ((this.catalog == null)) "<null>" else this.catalog))
        sb.append(',')
        sb.append("state")
        sb.append('=')
        sb.append((if ((this.state == null)) "<null>" else this.state))
        sb.append(',')
        sb.append("resourceRequirements")
        sb.append('=')
        sb.append((if ((this.resourceRequirements == null)) "<null>" else this.resourceRequirements))
        sb.append(',')
        sb.append("sourceResourceRequirements")
        sb.append('=')
        sb.append((if ((this.sourceResourceRequirements == null)) "<null>" else this.sourceResourceRequirements))
        sb.append(',')
        sb.append("destinationResourceRequirements")
        sb.append('=')
        sb.append((if ((this.destinationResourceRequirements == null)) "<null>" else this.destinationResourceRequirements))
        sb.append(',')
        sb.append("workspaceId")
        sb.append('=')
        sb.append((if ((this.workspaceId == null)) "<null>" else this.workspaceId))
        sb.append(',')
        sb.append("connectionId")
        sb.append('=')
        sb.append((if ((this.connectionId == null)) "<null>" else this.connectionId))
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
        result = ((result * 31) + (if ((this.sourceId == null)) 0 else sourceId.hashCode()))
        result = ((result * 31) + (if ((this.webhookOperationConfigs == null)) 0 else webhookOperationConfigs.hashCode()))
        result = ((result * 31) + (if ((this.operationSequence == null)) 0 else operationSequence.hashCode()))
        result = ((result * 31) + (if ((this.destinationResourceRequirements == null)) 0 else destinationResourceRequirements.hashCode()))
        result = ((result * 31) + (if ((this.prefix == null)) 0 else prefix.hashCode()))
        result = ((result * 31) + (if ((this.catalog == null)) 0 else catalog.hashCode()))
        result = ((result * 31) + (if ((this.destinationId == null)) 0 else destinationId.hashCode()))
        result = ((result * 31) + (if ((this.namespaceDefinition == null)) 0 else namespaceDefinition.hashCode()))
        result = ((result * 31) + (if ((this.resourceRequirements == null)) 0 else resourceRequirements.hashCode()))
        result = ((result * 31) + (if ((this.destinationConfiguration == null)) 0 else destinationConfiguration.hashCode()))
        result = ((result * 31) + (if ((this.sourceConfiguration == null)) 0 else sourceConfiguration.hashCode()))
        result = ((result * 31) + (if ((this.sourceResourceRequirements == null)) 0 else sourceResourceRequirements.hashCode()))
        result = ((result * 31) + (if ((this.namespaceFormat == null)) 0 else namespaceFormat.hashCode()))
        result = ((result * 31) + (if ((this.connectionId == null)) 0 else connectionId.hashCode()))
        result = ((result * 31) + (if ((this.state == null)) 0 else state.hashCode()))
        result = ((result * 31) + (if ((this.workspaceId == null)) 0 else workspaceId.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is StandardSyncInput) == false) {
            return false
        }
        val rhs = other
        return (((((((((((((((((this.sourceId === rhs.sourceId) || ((this.sourceId != null) && (this.sourceId == rhs.sourceId))) && ((this.webhookOperationConfigs === rhs.webhookOperationConfigs) || ((this.webhookOperationConfigs != null) && (this.webhookOperationConfigs == rhs.webhookOperationConfigs)))) && ((this.operationSequence === rhs.operationSequence) || ((this.operationSequence != null) && (this.operationSequence == rhs.operationSequence)))) && ((this.destinationResourceRequirements === rhs.destinationResourceRequirements) || ((this.destinationResourceRequirements != null) && (this.destinationResourceRequirements == rhs.destinationResourceRequirements)))) && ((this.prefix === rhs.prefix) || ((this.prefix != null) && (this.prefix == rhs.prefix)))) && ((this.catalog === rhs.catalog) || ((this.catalog != null) && (this.catalog == rhs.catalog)))) && ((this.destinationId === rhs.destinationId) || ((this.destinationId != null) && (this.destinationId == rhs.destinationId)))) && ((this.namespaceDefinition == rhs.namespaceDefinition) || ((this.namespaceDefinition != null) && (this.namespaceDefinition == rhs.namespaceDefinition)))) && ((this.resourceRequirements === rhs.resourceRequirements) || ((this.resourceRequirements != null) && (this.resourceRequirements == rhs.resourceRequirements)))) && ((this.destinationConfiguration === rhs.destinationConfiguration) || ((this.destinationConfiguration != null) && (this.destinationConfiguration == rhs.destinationConfiguration)))) && ((this.sourceConfiguration === rhs.sourceConfiguration) || ((this.sourceConfiguration != null) && (this.sourceConfiguration == rhs.sourceConfiguration)))) && ((this.sourceResourceRequirements === rhs.sourceResourceRequirements) || ((this.sourceResourceRequirements != null) && (this.sourceResourceRequirements == rhs.sourceResourceRequirements)))) && ((this.namespaceFormat === rhs.namespaceFormat) || ((this.namespaceFormat != null) && (this.namespaceFormat == rhs.namespaceFormat)))) && ((this.connectionId === rhs.connectionId) || ((this.connectionId != null) && (this.connectionId == rhs.connectionId)))) && ((this.state === rhs.state) || ((this.state != null) && (this.state == rhs.state)))) && ((this.workspaceId === rhs.workspaceId) || ((this.workspaceId != null) && (this.workspaceId == rhs.workspaceId))))
    }

    companion object {
        private const val serialVersionUID = 7598246014468300732L
    }
}
