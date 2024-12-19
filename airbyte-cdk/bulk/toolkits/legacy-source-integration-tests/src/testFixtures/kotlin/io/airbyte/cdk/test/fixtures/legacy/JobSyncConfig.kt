package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.*
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog
import java.io.Serializable
import java.util.*

/**
 * JobSyncConfig
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
    "configuredAirbyteCatalog",
    "sourceDockerImage",
    "sourceProtocolVersion",
    "destinationDockerImage",
    "destinationProtocolVersion",
    "sourceResourceRequirements",
    "destinationResourceRequirements",
    "operationSequence",
    "webhookOperationConfigs",
    "resourceRequirements",
    "isSourceCustomConnector",
    "isDestinationCustomConnector",
    "workspaceId"
)
class JobSyncConfig : Serializable {
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
    var namespaceDefinition: NamespaceDefinitionType? = NamespaceDefinitionType.fromValue("source")

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
    @get:JsonProperty("configuredAirbyteCatalog")
    @set:JsonProperty("configuredAirbyteCatalog")
    @JsonProperty("configuredAirbyteCatalog")
    @JsonPropertyDescription("the configured airbyte catalog")
    var configuredAirbyteCatalog: ConfiguredAirbyteCatalog? = null
    /**
     * Image name of the source with tag.
     * (Required)
     *
     */
    /**
     * Image name of the source with tag.
     * (Required)
     *
     */
    /**
     * Image name of the source with tag.
     * (Required)
     *
     */
    @get:JsonProperty("sourceDockerImage")
    @set:JsonProperty("sourceDockerImage")
    @JsonProperty("sourceDockerImage")
    @JsonPropertyDescription("Image name of the source with tag.")
    var sourceDockerImage: String? = null
    /**
     * Airbyte Protocol Version of the source
     *
     */
    /**
     * Airbyte Protocol Version of the source
     *
     */
    /**
     * Airbyte Protocol Version of the source
     *
     */
    @get:JsonProperty("sourceProtocolVersion")
    @set:JsonProperty("sourceProtocolVersion")
    @JsonProperty("sourceProtocolVersion")
    @JsonPropertyDescription("Airbyte Protocol Version of the source")
    var sourceProtocolVersion: Version? = null
    /**
     * Image name of the destination with tag.
     * (Required)
     *
     */
    /**
     * Image name of the destination with tag.
     * (Required)
     *
     */
    /**
     * Image name of the destination with tag.
     * (Required)
     *
     */
    @get:JsonProperty("destinationDockerImage")
    @set:JsonProperty("destinationDockerImage")
    @JsonProperty("destinationDockerImage")
    @JsonPropertyDescription("Image name of the destination with tag.")
    var destinationDockerImage: String? = null
    /**
     * Airbyte Protocol Version of the destination
     *
     */
    /**
     * Airbyte Protocol Version of the destination
     *
     */
    /**
     * Airbyte Protocol Version of the destination
     *
     */
    @get:JsonProperty("destinationProtocolVersion")
    @set:JsonProperty("destinationProtocolVersion")
    @JsonProperty("destinationProtocolVersion")
    @JsonPropertyDescription("Airbyte Protocol Version of the destination")
    var destinationProtocolVersion: Version? = null
    /**
     * optional resource requirements to use in source container - this is used instead of `resourceRequirements` for the source container
     *
     */
    /**
     * optional resource requirements to use in source container - this is used instead of `resourceRequirements` for the source container
     *
     */
    /**
     * optional resource requirements to use in source container - this is used instead of `resourceRequirements` for the source container
     *
     */
    @get:JsonProperty("sourceResourceRequirements")
    @set:JsonProperty("sourceResourceRequirements")
    @JsonProperty("sourceResourceRequirements")
    @JsonPropertyDescription("optional resource requirements to use in source container - this is used instead of `resourceRequirements` for the source container")
    var sourceResourceRequirements: ResourceRequirements? = null
    /**
     * optional resource requirements to use in dest container - this is used instead of `resourceRequirements` for the dest container
     *
     */
    /**
     * optional resource requirements to use in dest container - this is used instead of `resourceRequirements` for the dest container
     *
     */
    /**
     * optional resource requirements to use in dest container - this is used instead of `resourceRequirements` for the dest container
     *
     */
    @get:JsonProperty("destinationResourceRequirements")
    @set:JsonProperty("destinationResourceRequirements")
    @JsonProperty("destinationResourceRequirements")
    @JsonPropertyDescription("optional resource requirements to use in dest container - this is used instead of `resourceRequirements` for the dest container")
    var destinationResourceRequirements: ResourceRequirements? = null
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
     * The webhook operation configs belonging to this workspace. Must conform to WebhookOperationConfigs.yaml.
     *
     */
    /**
     * The webhook operation configs belonging to this workspace. Must conform to WebhookOperationConfigs.yaml.
     *
     */
    /**
     * The webhook operation configs belonging to this workspace. Must conform to WebhookOperationConfigs.yaml.
     *
     */
    @get:JsonProperty("webhookOperationConfigs")
    @set:JsonProperty("webhookOperationConfigs")
    @JsonProperty("webhookOperationConfigs")
    @JsonPropertyDescription("The webhook operation configs belonging to this workspace. Must conform to WebhookOperationConfigs.yaml.")
    var webhookOperationConfigs: JsonNode? = null
    /**
     * optional resource requirements to run sync workers - this is used for containers other than the source/dest containers
     *
     */
    /**
     * optional resource requirements to run sync workers - this is used for containers other than the source/dest containers
     *
     */
    /**
     * optional resource requirements to run sync workers - this is used for containers other than the source/dest containers
     *
     */
    @get:JsonProperty("resourceRequirements")
    @set:JsonProperty("resourceRequirements")
    @JsonProperty("resourceRequirements")
    @JsonPropertyDescription("optional resource requirements to run sync workers - this is used for containers other than the source/dest containers")
    var resourceRequirements: ResourceRequirements? = null
    /**
     * determine if the source running image is a custom connector.
     *
     */
    /**
     * determine if the source running image is a custom connector.
     *
     */
    /**
     * determine if the source running image is a custom connector.
     *
     */
    @get:JsonProperty("isSourceCustomConnector")
    @set:JsonProperty("isSourceCustomConnector")
    @JsonProperty("isSourceCustomConnector")
    @JsonPropertyDescription("determine if the source running image is a custom connector.")
    var isSourceCustomConnector: Boolean? = null
    /**
     * determine if the destination running image is a custom connector.
     *
     */
    /**
     * determine if the destination running image is a custom connector.
     *
     */
    /**
     * determine if the destination running image is a custom connector.
     *
     */
    @get:JsonProperty("isDestinationCustomConnector")
    @set:JsonProperty("isDestinationCustomConnector")
    @JsonProperty("isDestinationCustomConnector")
    @JsonPropertyDescription("determine if the destination running image is a custom connector.")
    var isDestinationCustomConnector: Boolean? = null
    /**
     * The id of the workspace associated with the sync
     *
     */
    /**
     * The id of the workspace associated with the sync
     *
     */
    /**
     * The id of the workspace associated with the sync
     *
     */
    @get:JsonProperty("workspaceId")
    @set:JsonProperty("workspaceId")
    @JsonProperty("workspaceId")
    @JsonPropertyDescription("The id of the workspace associated with the sync")
    var workspaceId: UUID? = null

    fun withNamespaceDefinition(namespaceDefinition: NamespaceDefinitionType?): JobSyncConfig {
        this.namespaceDefinition = namespaceDefinition
        return this
    }

    fun withNamespaceFormat(namespaceFormat: String?): JobSyncConfig {
        this.namespaceFormat = namespaceFormat
        return this
    }

    fun withPrefix(prefix: String?): JobSyncConfig {
        this.prefix = prefix
        return this
    }

    fun withConfiguredAirbyteCatalog(configuredAirbyteCatalog: ConfiguredAirbyteCatalog?): JobSyncConfig {
        this.configuredAirbyteCatalog = configuredAirbyteCatalog
        return this
    }

    fun withSourceDockerImage(sourceDockerImage: String?): JobSyncConfig {
        this.sourceDockerImage = sourceDockerImage
        return this
    }

    fun withSourceProtocolVersion(sourceProtocolVersion: Version?): JobSyncConfig {
        this.sourceProtocolVersion = sourceProtocolVersion
        return this
    }

    fun withDestinationDockerImage(destinationDockerImage: String?): JobSyncConfig {
        this.destinationDockerImage = destinationDockerImage
        return this
    }

    fun withDestinationProtocolVersion(destinationProtocolVersion: Version?): JobSyncConfig {
        this.destinationProtocolVersion = destinationProtocolVersion
        return this
    }

    fun withSourceResourceRequirements(sourceResourceRequirements: ResourceRequirements?): JobSyncConfig {
        this.sourceResourceRequirements = sourceResourceRequirements
        return this
    }

    fun withDestinationResourceRequirements(destinationResourceRequirements: ResourceRequirements?): JobSyncConfig {
        this.destinationResourceRequirements = destinationResourceRequirements
        return this
    }

    fun withOperationSequence(operationSequence: List<StandardSyncOperation>?): JobSyncConfig {
        this.operationSequence = operationSequence
        return this
    }

    fun withWebhookOperationConfigs(webhookOperationConfigs: JsonNode?): JobSyncConfig {
        this.webhookOperationConfigs = webhookOperationConfigs
        return this
    }

    fun withResourceRequirements(resourceRequirements: ResourceRequirements?): JobSyncConfig {
        this.resourceRequirements = resourceRequirements
        return this
    }

    fun withIsSourceCustomConnector(isSourceCustomConnector: Boolean?): JobSyncConfig {
        this.isSourceCustomConnector = isSourceCustomConnector
        return this
    }

    fun withIsDestinationCustomConnector(isDestinationCustomConnector: Boolean?): JobSyncConfig {
        this.isDestinationCustomConnector = isDestinationCustomConnector
        return this
    }

    fun withWorkspaceId(workspaceId: UUID?): JobSyncConfig {
        this.workspaceId = workspaceId
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(JobSyncConfig::class.java.name).append('@').append(
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
        sb.append("configuredAirbyteCatalog")
        sb.append('=')
        sb.append((if ((this.configuredAirbyteCatalog == null)) "<null>" else this.configuredAirbyteCatalog))
        sb.append(',')
        sb.append("sourceDockerImage")
        sb.append('=')
        sb.append((if ((this.sourceDockerImage == null)) "<null>" else this.sourceDockerImage))
        sb.append(',')
        sb.append("sourceProtocolVersion")
        sb.append('=')
        sb.append((if ((this.sourceProtocolVersion == null)) "<null>" else this.sourceProtocolVersion))
        sb.append(',')
        sb.append("destinationDockerImage")
        sb.append('=')
        sb.append((if ((this.destinationDockerImage == null)) "<null>" else this.destinationDockerImage))
        sb.append(',')
        sb.append("destinationProtocolVersion")
        sb.append('=')
        sb.append((if ((this.destinationProtocolVersion == null)) "<null>" else this.destinationProtocolVersion))
        sb.append(',')
        sb.append("sourceResourceRequirements")
        sb.append('=')
        sb.append((if ((this.sourceResourceRequirements == null)) "<null>" else this.sourceResourceRequirements))
        sb.append(',')
        sb.append("destinationResourceRequirements")
        sb.append('=')
        sb.append((if ((this.destinationResourceRequirements == null)) "<null>" else this.destinationResourceRequirements))
        sb.append(',')
        sb.append("operationSequence")
        sb.append('=')
        sb.append((if ((this.operationSequence == null)) "<null>" else this.operationSequence))
        sb.append(',')
        sb.append("webhookOperationConfigs")
        sb.append('=')
        sb.append((if ((this.webhookOperationConfigs == null)) "<null>" else this.webhookOperationConfigs))
        sb.append(',')
        sb.append("resourceRequirements")
        sb.append('=')
        sb.append((if ((this.resourceRequirements == null)) "<null>" else this.resourceRequirements))
        sb.append(',')
        sb.append("isSourceCustomConnector")
        sb.append('=')
        sb.append((if ((this.isSourceCustomConnector == null)) "<null>" else this.isSourceCustomConnector))
        sb.append(',')
        sb.append("isDestinationCustomConnector")
        sb.append('=')
        sb.append((if ((this.isDestinationCustomConnector == null)) "<null>" else this.isDestinationCustomConnector))
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
        result = ((result * 31) + (if ((this.webhookOperationConfigs == null)) 0 else webhookOperationConfigs.hashCode()))
        result = ((result * 31) + (if ((this.destinationResourceRequirements == null)) 0 else destinationResourceRequirements.hashCode()))
        result = ((result * 31) + (if ((this.operationSequence == null)) 0 else operationSequence.hashCode()))
        result = ((result * 31) + (if ((this.destinationProtocolVersion == null)) 0 else destinationProtocolVersion.hashCode()))
        result = ((result * 31) + (if ((this.sourceProtocolVersion == null)) 0 else sourceProtocolVersion.hashCode()))
        result = ((result * 31) + (if ((this.prefix == null)) 0 else prefix.hashCode()))
        result = ((result * 31) + (if ((this.configuredAirbyteCatalog == null)) 0 else configuredAirbyteCatalog.hashCode()))
        result = ((result * 31) + (if ((this.isDestinationCustomConnector == null)) 0 else isDestinationCustomConnector.hashCode()))
        result = ((result * 31) + (if ((this.namespaceDefinition == null)) 0 else namespaceDefinition.hashCode()))
        result = ((result * 31) + (if ((this.destinationDockerImage == null)) 0 else destinationDockerImage.hashCode()))
        result = ((result * 31) + (if ((this.resourceRequirements == null)) 0 else resourceRequirements.hashCode()))
        result = ((result * 31) + (if ((this.isSourceCustomConnector == null)) 0 else isSourceCustomConnector.hashCode()))
        result = ((result * 31) + (if ((this.sourceResourceRequirements == null)) 0 else sourceResourceRequirements.hashCode()))
        result = ((result * 31) + (if ((this.namespaceFormat == null)) 0 else namespaceFormat.hashCode()))
        result = ((result * 31) + (if ((this.sourceDockerImage == null)) 0 else sourceDockerImage.hashCode()))
        result = ((result * 31) + (if ((this.workspaceId == null)) 0 else workspaceId.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is JobSyncConfig) == false) {
            return false
        }
        val rhs = other
        return (((((((((((((((((this.webhookOperationConfigs === rhs.webhookOperationConfigs) || ((this.webhookOperationConfigs != null) && (this.webhookOperationConfigs == rhs.webhookOperationConfigs))) && ((this.destinationResourceRequirements === rhs.destinationResourceRequirements) || ((this.destinationResourceRequirements != null) && (this.destinationResourceRequirements == rhs.destinationResourceRequirements)))) && ((this.operationSequence === rhs.operationSequence) || ((this.operationSequence != null) && (this.operationSequence == rhs.operationSequence)))) && ((this.destinationProtocolVersion === rhs.destinationProtocolVersion) || ((this.destinationProtocolVersion != null) && destinationProtocolVersion!!.equals(
            rhs.destinationProtocolVersion
        )))) && ((this.sourceProtocolVersion === rhs.sourceProtocolVersion) || ((this.sourceProtocolVersion != null) && sourceProtocolVersion!!.equals(
            rhs.sourceProtocolVersion
        )))) && ((this.prefix === rhs.prefix) || ((this.prefix != null) && (this.prefix == rhs.prefix)))) && ((this.configuredAirbyteCatalog === rhs.configuredAirbyteCatalog) || ((this.configuredAirbyteCatalog != null) && (this.configuredAirbyteCatalog == rhs.configuredAirbyteCatalog)))) && ((this.isDestinationCustomConnector === rhs.isDestinationCustomConnector) || ((this.isDestinationCustomConnector != null) && (this.isDestinationCustomConnector == rhs.isDestinationCustomConnector)))) && ((this.namespaceDefinition == rhs.namespaceDefinition) || ((this.namespaceDefinition != null) && (this.namespaceDefinition == rhs.namespaceDefinition)))) && ((this.destinationDockerImage === rhs.destinationDockerImage) || ((this.destinationDockerImage != null) && (this.destinationDockerImage == rhs.destinationDockerImage)))) && ((this.resourceRequirements === rhs.resourceRequirements) || ((this.resourceRequirements != null) && (this.resourceRequirements == rhs.resourceRequirements)))) && ((this.isSourceCustomConnector === rhs.isSourceCustomConnector) || ((this.isSourceCustomConnector != null) && (this.isSourceCustomConnector == rhs.isSourceCustomConnector)))) && ((this.sourceResourceRequirements === rhs.sourceResourceRequirements) || ((this.sourceResourceRequirements != null) && (this.sourceResourceRequirements == rhs.sourceResourceRequirements)))) && ((this.namespaceFormat === rhs.namespaceFormat) || ((this.namespaceFormat != null) && (this.namespaceFormat == rhs.namespaceFormat)))) && ((this.sourceDockerImage === rhs.sourceDockerImage) || ((this.sourceDockerImage != null) && (this.sourceDockerImage == rhs.sourceDockerImage)))) && ((this.workspaceId === rhs.workspaceId) || ((this.workspaceId != null) && (this.workspaceId == rhs.workspaceId))))
    }


    /**
     * Namespace Definition
     *
     *
     * Method used for computing final namespace in destination
     *
     */
    enum class NamespaceDefinitionType(private val value: String) {
        SOURCE("source"),
        DESTINATION("destination"),
        CUSTOMFORMAT("customformat");

        override fun toString(): String {
            return this.value
        }

        @JsonValue
        fun value(): String {
            return this.value
        }

        companion object {
            private val CONSTANTS: MutableMap<String, NamespaceDefinitionType> = HashMap()

            init {
                for (c in entries) {
                    CONSTANTS[c.value] = c
                }
            }

            @JsonCreator
            fun fromValue(value: String): NamespaceDefinitionType {
                val constant = CONSTANTS[value]
                requireNotNull(constant) { value }
                return constant
            }
        }
    }

    companion object {
        private const val serialVersionUID = -2037536085433975701L
    }
}
