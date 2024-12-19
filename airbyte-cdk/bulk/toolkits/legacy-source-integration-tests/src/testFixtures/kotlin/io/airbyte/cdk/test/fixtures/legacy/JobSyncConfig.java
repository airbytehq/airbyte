
package io.airbyte.cdk.test.fixtures.legacy;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import com.fasterxml.jackson.annotation.JsonValue;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * JobSyncConfig
 * <p>
 * job sync config
 *
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
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
})
public class JobSyncConfig implements Serializable
{

    /**
     * Namespace Definition
     * <p>
     * Method used for computing final namespace in destination
     *
     */
    @JsonProperty("namespaceDefinition")
    @JsonPropertyDescription("Method used for computing final namespace in destination")
    private JobSyncConfig.NamespaceDefinitionType namespaceDefinition = JobSyncConfig.NamespaceDefinitionType.fromValue("source");
    @JsonProperty("namespaceFormat")
    private String namespaceFormat = null;
    /**
     * Prefix that will be prepended to the name of each stream when it is written to the destination.
     *
     */
    @JsonProperty("prefix")
    @JsonPropertyDescription("Prefix that will be prepended to the name of each stream when it is written to the destination.")
    private String prefix;
    /**
     * the configured airbyte catalog
     * (Required)
     *
     */
    @JsonProperty("configuredAirbyteCatalog")
    @JsonPropertyDescription("the configured airbyte catalog")
    private ConfiguredAirbyteCatalog configuredAirbyteCatalog;
    /**
     * Image name of the source with tag.
     * (Required)
     *
     */
    @JsonProperty("sourceDockerImage")
    @JsonPropertyDescription("Image name of the source with tag.")
    private String sourceDockerImage;
    /**
     * Airbyte Protocol Version of the source
     *
     */
    @JsonProperty("sourceProtocolVersion")
    @JsonPropertyDescription("Airbyte Protocol Version of the source")
    private Version sourceProtocolVersion;
    /**
     * Image name of the destination with tag.
     * (Required)
     *
     */
    @JsonProperty("destinationDockerImage")
    @JsonPropertyDescription("Image name of the destination with tag.")
    private String destinationDockerImage;
    /**
     * Airbyte Protocol Version of the destination
     *
     */
    @JsonProperty("destinationProtocolVersion")
    @JsonPropertyDescription("Airbyte Protocol Version of the destination")
    private Version destinationProtocolVersion;
    /**
     * optional resource requirements to use in source container - this is used instead of `resourceRequirements` for the source container
     *
     */
    @JsonProperty("sourceResourceRequirements")
    @JsonPropertyDescription("optional resource requirements to use in source container - this is used instead of `resourceRequirements` for the source container")
    private ResourceRequirements sourceResourceRequirements;
    /**
     * optional resource requirements to use in dest container - this is used instead of `resourceRequirements` for the dest container
     *
     */
    @JsonProperty("destinationResourceRequirements")
    @JsonPropertyDescription("optional resource requirements to use in dest container - this is used instead of `resourceRequirements` for the dest container")
    private ResourceRequirements destinationResourceRequirements;
    /**
     * Sequence of configurations of operations to apply as part of the sync
     *
     */
    @JsonProperty("operationSequence")
    @JsonPropertyDescription("Sequence of configurations of operations to apply as part of the sync")
    private List<StandardSyncOperation> operationSequence = new ArrayList<StandardSyncOperation>();
    /**
     * The webhook operation configs belonging to this workspace. Must conform to WebhookOperationConfigs.yaml.
     *
     */
    @JsonProperty("webhookOperationConfigs")
    @JsonPropertyDescription("The webhook operation configs belonging to this workspace. Must conform to WebhookOperationConfigs.yaml.")
    private JsonNode webhookOperationConfigs;
    /**
     * optional resource requirements to run sync workers - this is used for containers other than the source/dest containers
     *
     */
    @JsonProperty("resourceRequirements")
    @JsonPropertyDescription("optional resource requirements to run sync workers - this is used for containers other than the source/dest containers")
    private ResourceRequirements resourceRequirements;
    /**
     * determine if the source running image is a custom connector.
     *
     */
    @JsonProperty("isSourceCustomConnector")
    @JsonPropertyDescription("determine if the source running image is a custom connector.")
    private Boolean isSourceCustomConnector;
    /**
     * determine if the destination running image is a custom connector.
     *
     */
    @JsonProperty("isDestinationCustomConnector")
    @JsonPropertyDescription("determine if the destination running image is a custom connector.")
    private Boolean isDestinationCustomConnector;
    /**
     * The id of the workspace associated with the sync
     *
     */
    @JsonProperty("workspaceId")
    @JsonPropertyDescription("The id of the workspace associated with the sync")
    private UUID workspaceId;
    private final static long serialVersionUID = -2037536085433975701L;

    /**
     * Namespace Definition
     * <p>
     * Method used for computing final namespace in destination
     *
     */
    @JsonProperty("namespaceDefinition")
    public JobSyncConfig.NamespaceDefinitionType getNamespaceDefinition() {
        return namespaceDefinition;
    }

    /**
     * Namespace Definition
     * <p>
     * Method used for computing final namespace in destination
     *
     */
    @JsonProperty("namespaceDefinition")
    public void setNamespaceDefinition(JobSyncConfig.NamespaceDefinitionType namespaceDefinition) {
        this.namespaceDefinition = namespaceDefinition;
    }

    public JobSyncConfig withNamespaceDefinition(JobSyncConfig.NamespaceDefinitionType namespaceDefinition) {
        this.namespaceDefinition = namespaceDefinition;
        return this;
    }

    @JsonProperty("namespaceFormat")
    public String getNamespaceFormat() {
        return namespaceFormat;
    }

    @JsonProperty("namespaceFormat")
    public void setNamespaceFormat(String namespaceFormat) {
        this.namespaceFormat = namespaceFormat;
    }

    public JobSyncConfig withNamespaceFormat(String namespaceFormat) {
        this.namespaceFormat = namespaceFormat;
        return this;
    }

    /**
     * Prefix that will be prepended to the name of each stream when it is written to the destination.
     *
     */
    @JsonProperty("prefix")
    public String getPrefix() {
        return prefix;
    }

    /**
     * Prefix that will be prepended to the name of each stream when it is written to the destination.
     *
     */
    @JsonProperty("prefix")
    public void setPrefix(String prefix) {
        this.prefix = prefix;
    }

    public JobSyncConfig withPrefix(String prefix) {
        this.prefix = prefix;
        return this;
    }

    /**
     * the configured airbyte catalog
     * (Required)
     *
     */
    @JsonProperty("configuredAirbyteCatalog")
    public ConfiguredAirbyteCatalog getConfiguredAirbyteCatalog() {
        return configuredAirbyteCatalog;
    }

    /**
     * the configured airbyte catalog
     * (Required)
     *
     */
    @JsonProperty("configuredAirbyteCatalog")
    public void setConfiguredAirbyteCatalog(ConfiguredAirbyteCatalog configuredAirbyteCatalog) {
        this.configuredAirbyteCatalog = configuredAirbyteCatalog;
    }

    public JobSyncConfig withConfiguredAirbyteCatalog(ConfiguredAirbyteCatalog configuredAirbyteCatalog) {
        this.configuredAirbyteCatalog = configuredAirbyteCatalog;
        return this;
    }

    /**
     * Image name of the source with tag.
     * (Required)
     *
     */
    @JsonProperty("sourceDockerImage")
    public String getSourceDockerImage() {
        return sourceDockerImage;
    }

    /**
     * Image name of the source with tag.
     * (Required)
     *
     */
    @JsonProperty("sourceDockerImage")
    public void setSourceDockerImage(String sourceDockerImage) {
        this.sourceDockerImage = sourceDockerImage;
    }

    public JobSyncConfig withSourceDockerImage(String sourceDockerImage) {
        this.sourceDockerImage = sourceDockerImage;
        return this;
    }

    /**
     * Airbyte Protocol Version of the source
     *
     */
    @JsonProperty("sourceProtocolVersion")
    public Version getSourceProtocolVersion() {
        return sourceProtocolVersion;
    }

    /**
     * Airbyte Protocol Version of the source
     *
     */
    @JsonProperty("sourceProtocolVersion")
    public void setSourceProtocolVersion(Version sourceProtocolVersion) {
        this.sourceProtocolVersion = sourceProtocolVersion;
    }

    public JobSyncConfig withSourceProtocolVersion(Version sourceProtocolVersion) {
        this.sourceProtocolVersion = sourceProtocolVersion;
        return this;
    }

    /**
     * Image name of the destination with tag.
     * (Required)
     *
     */
    @JsonProperty("destinationDockerImage")
    public String getDestinationDockerImage() {
        return destinationDockerImage;
    }

    /**
     * Image name of the destination with tag.
     * (Required)
     *
     */
    @JsonProperty("destinationDockerImage")
    public void setDestinationDockerImage(String destinationDockerImage) {
        this.destinationDockerImage = destinationDockerImage;
    }

    public JobSyncConfig withDestinationDockerImage(String destinationDockerImage) {
        this.destinationDockerImage = destinationDockerImage;
        return this;
    }

    /**
     * Airbyte Protocol Version of the destination
     *
     */
    @JsonProperty("destinationProtocolVersion")
    public Version getDestinationProtocolVersion() {
        return destinationProtocolVersion;
    }

    /**
     * Airbyte Protocol Version of the destination
     *
     */
    @JsonProperty("destinationProtocolVersion")
    public void setDestinationProtocolVersion(Version destinationProtocolVersion) {
        this.destinationProtocolVersion = destinationProtocolVersion;
    }

    public JobSyncConfig withDestinationProtocolVersion(Version destinationProtocolVersion) {
        this.destinationProtocolVersion = destinationProtocolVersion;
        return this;
    }

    /**
     * optional resource requirements to use in source container - this is used instead of `resourceRequirements` for the source container
     *
     */
    @JsonProperty("sourceResourceRequirements")
    public ResourceRequirements getSourceResourceRequirements() {
        return sourceResourceRequirements;
    }

    /**
     * optional resource requirements to use in source container - this is used instead of `resourceRequirements` for the source container
     *
     */
    @JsonProperty("sourceResourceRequirements")
    public void setSourceResourceRequirements(ResourceRequirements sourceResourceRequirements) {
        this.sourceResourceRequirements = sourceResourceRequirements;
    }

    public JobSyncConfig withSourceResourceRequirements(ResourceRequirements sourceResourceRequirements) {
        this.sourceResourceRequirements = sourceResourceRequirements;
        return this;
    }

    /**
     * optional resource requirements to use in dest container - this is used instead of `resourceRequirements` for the dest container
     *
     */
    @JsonProperty("destinationResourceRequirements")
    public ResourceRequirements getDestinationResourceRequirements() {
        return destinationResourceRequirements;
    }

    /**
     * optional resource requirements to use in dest container - this is used instead of `resourceRequirements` for the dest container
     *
     */
    @JsonProperty("destinationResourceRequirements")
    public void setDestinationResourceRequirements(ResourceRequirements destinationResourceRequirements) {
        this.destinationResourceRequirements = destinationResourceRequirements;
    }

    public JobSyncConfig withDestinationResourceRequirements(ResourceRequirements destinationResourceRequirements) {
        this.destinationResourceRequirements = destinationResourceRequirements;
        return this;
    }

    /**
     * Sequence of configurations of operations to apply as part of the sync
     *
     */
    @JsonProperty("operationSequence")
    public List<StandardSyncOperation> getOperationSequence() {
        return operationSequence;
    }

    /**
     * Sequence of configurations of operations to apply as part of the sync
     *
     */
    @JsonProperty("operationSequence")
    public void setOperationSequence(List<StandardSyncOperation> operationSequence) {
        this.operationSequence = operationSequence;
    }

    public JobSyncConfig withOperationSequence(List<StandardSyncOperation> operationSequence) {
        this.operationSequence = operationSequence;
        return this;
    }

    /**
     * The webhook operation configs belonging to this workspace. Must conform to WebhookOperationConfigs.yaml.
     *
     */
    @JsonProperty("webhookOperationConfigs")
    public JsonNode getWebhookOperationConfigs() {
        return webhookOperationConfigs;
    }

    /**
     * The webhook operation configs belonging to this workspace. Must conform to WebhookOperationConfigs.yaml.
     *
     */
    @JsonProperty("webhookOperationConfigs")
    public void setWebhookOperationConfigs(JsonNode webhookOperationConfigs) {
        this.webhookOperationConfigs = webhookOperationConfigs;
    }

    public JobSyncConfig withWebhookOperationConfigs(JsonNode webhookOperationConfigs) {
        this.webhookOperationConfigs = webhookOperationConfigs;
        return this;
    }

    /**
     * optional resource requirements to run sync workers - this is used for containers other than the source/dest containers
     *
     */
    @JsonProperty("resourceRequirements")
    public ResourceRequirements getResourceRequirements() {
        return resourceRequirements;
    }

    /**
     * optional resource requirements to run sync workers - this is used for containers other than the source/dest containers
     *
     */
    @JsonProperty("resourceRequirements")
    public void setResourceRequirements(ResourceRequirements resourceRequirements) {
        this.resourceRequirements = resourceRequirements;
    }

    public JobSyncConfig withResourceRequirements(ResourceRequirements resourceRequirements) {
        this.resourceRequirements = resourceRequirements;
        return this;
    }

    /**
     * determine if the source running image is a custom connector.
     *
     */
    @JsonProperty("isSourceCustomConnector")
    public Boolean getIsSourceCustomConnector() {
        return isSourceCustomConnector;
    }

    /**
     * determine if the source running image is a custom connector.
     *
     */
    @JsonProperty("isSourceCustomConnector")
    public void setIsSourceCustomConnector(Boolean isSourceCustomConnector) {
        this.isSourceCustomConnector = isSourceCustomConnector;
    }

    public JobSyncConfig withIsSourceCustomConnector(Boolean isSourceCustomConnector) {
        this.isSourceCustomConnector = isSourceCustomConnector;
        return this;
    }

    /**
     * determine if the destination running image is a custom connector.
     *
     */
    @JsonProperty("isDestinationCustomConnector")
    public Boolean getIsDestinationCustomConnector() {
        return isDestinationCustomConnector;
    }

    /**
     * determine if the destination running image is a custom connector.
     *
     */
    @JsonProperty("isDestinationCustomConnector")
    public void setIsDestinationCustomConnector(Boolean isDestinationCustomConnector) {
        this.isDestinationCustomConnector = isDestinationCustomConnector;
    }

    public JobSyncConfig withIsDestinationCustomConnector(Boolean isDestinationCustomConnector) {
        this.isDestinationCustomConnector = isDestinationCustomConnector;
        return this;
    }

    /**
     * The id of the workspace associated with the sync
     *
     */
    @JsonProperty("workspaceId")
    public UUID getWorkspaceId() {
        return workspaceId;
    }

    /**
     * The id of the workspace associated with the sync
     *
     */
    @JsonProperty("workspaceId")
    public void setWorkspaceId(UUID workspaceId) {
        this.workspaceId = workspaceId;
    }

    public JobSyncConfig withWorkspaceId(UUID workspaceId) {
        this.workspaceId = workspaceId;
        return this;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(JobSyncConfig.class.getName()).append('@').append(Integer.toHexString(System.identityHashCode(this))).append('[');
        sb.append("namespaceDefinition");
        sb.append('=');
        sb.append(((this.namespaceDefinition == null)?"<null>":this.namespaceDefinition));
        sb.append(',');
        sb.append("namespaceFormat");
        sb.append('=');
        sb.append(((this.namespaceFormat == null)?"<null>":this.namespaceFormat));
        sb.append(',');
        sb.append("prefix");
        sb.append('=');
        sb.append(((this.prefix == null)?"<null>":this.prefix));
        sb.append(',');
        sb.append("configuredAirbyteCatalog");
        sb.append('=');
        sb.append(((this.configuredAirbyteCatalog == null)?"<null>":this.configuredAirbyteCatalog));
        sb.append(',');
        sb.append("sourceDockerImage");
        sb.append('=');
        sb.append(((this.sourceDockerImage == null)?"<null>":this.sourceDockerImage));
        sb.append(',');
        sb.append("sourceProtocolVersion");
        sb.append('=');
        sb.append(((this.sourceProtocolVersion == null)?"<null>":this.sourceProtocolVersion));
        sb.append(',');
        sb.append("destinationDockerImage");
        sb.append('=');
        sb.append(((this.destinationDockerImage == null)?"<null>":this.destinationDockerImage));
        sb.append(',');
        sb.append("destinationProtocolVersion");
        sb.append('=');
        sb.append(((this.destinationProtocolVersion == null)?"<null>":this.destinationProtocolVersion));
        sb.append(',');
        sb.append("sourceResourceRequirements");
        sb.append('=');
        sb.append(((this.sourceResourceRequirements == null)?"<null>":this.sourceResourceRequirements));
        sb.append(',');
        sb.append("destinationResourceRequirements");
        sb.append('=');
        sb.append(((this.destinationResourceRequirements == null)?"<null>":this.destinationResourceRequirements));
        sb.append(',');
        sb.append("operationSequence");
        sb.append('=');
        sb.append(((this.operationSequence == null)?"<null>":this.operationSequence));
        sb.append(',');
        sb.append("webhookOperationConfigs");
        sb.append('=');
        sb.append(((this.webhookOperationConfigs == null)?"<null>":this.webhookOperationConfigs));
        sb.append(',');
        sb.append("resourceRequirements");
        sb.append('=');
        sb.append(((this.resourceRequirements == null)?"<null>":this.resourceRequirements));
        sb.append(',');
        sb.append("isSourceCustomConnector");
        sb.append('=');
        sb.append(((this.isSourceCustomConnector == null)?"<null>":this.isSourceCustomConnector));
        sb.append(',');
        sb.append("isDestinationCustomConnector");
        sb.append('=');
        sb.append(((this.isDestinationCustomConnector == null)?"<null>":this.isDestinationCustomConnector));
        sb.append(',');
        sb.append("workspaceId");
        sb.append('=');
        sb.append(((this.workspaceId == null)?"<null>":this.workspaceId));
        sb.append(',');
        if (sb.charAt((sb.length()- 1)) == ',') {
            sb.setCharAt((sb.length()- 1), ']');
        } else {
            sb.append(']');
        }
        return sb.toString();
    }

    @Override
    public int hashCode() {
        int result = 1;
        result = ((result* 31)+((this.webhookOperationConfigs == null)? 0 :this.webhookOperationConfigs.hashCode()));
        result = ((result* 31)+((this.destinationResourceRequirements == null)? 0 :this.destinationResourceRequirements.hashCode()));
        result = ((result* 31)+((this.operationSequence == null)? 0 :this.operationSequence.hashCode()));
        result = ((result* 31)+((this.destinationProtocolVersion == null)? 0 :this.destinationProtocolVersion.hashCode()));
        result = ((result* 31)+((this.sourceProtocolVersion == null)? 0 :this.sourceProtocolVersion.hashCode()));
        result = ((result* 31)+((this.prefix == null)? 0 :this.prefix.hashCode()));
        result = ((result* 31)+((this.configuredAirbyteCatalog == null)? 0 :this.configuredAirbyteCatalog.hashCode()));
        result = ((result* 31)+((this.isDestinationCustomConnector == null)? 0 :this.isDestinationCustomConnector.hashCode()));
        result = ((result* 31)+((this.namespaceDefinition == null)? 0 :this.namespaceDefinition.hashCode()));
        result = ((result* 31)+((this.destinationDockerImage == null)? 0 :this.destinationDockerImage.hashCode()));
        result = ((result* 31)+((this.resourceRequirements == null)? 0 :this.resourceRequirements.hashCode()));
        result = ((result* 31)+((this.isSourceCustomConnector == null)? 0 :this.isSourceCustomConnector.hashCode()));
        result = ((result* 31)+((this.sourceResourceRequirements == null)? 0 :this.sourceResourceRequirements.hashCode()));
        result = ((result* 31)+((this.namespaceFormat == null)? 0 :this.namespaceFormat.hashCode()));
        result = ((result* 31)+((this.sourceDockerImage == null)? 0 :this.sourceDockerImage.hashCode()));
        result = ((result* 31)+((this.workspaceId == null)? 0 :this.workspaceId.hashCode()));
        return result;
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof JobSyncConfig) == false) {
            return false;
        }
        JobSyncConfig rhs = ((JobSyncConfig) other);
        return (((((((((((((((((this.webhookOperationConfigs == rhs.webhookOperationConfigs)||((this.webhookOperationConfigs!= null)&&this.webhookOperationConfigs.equals(rhs.webhookOperationConfigs)))&&((this.destinationResourceRequirements == rhs.destinationResourceRequirements)||((this.destinationResourceRequirements!= null)&&this.destinationResourceRequirements.equals(rhs.destinationResourceRequirements))))&&((this.operationSequence == rhs.operationSequence)||((this.operationSequence!= null)&&this.operationSequence.equals(rhs.operationSequence))))&&((this.destinationProtocolVersion == rhs.destinationProtocolVersion)||((this.destinationProtocolVersion!= null)&&this.destinationProtocolVersion.equals(rhs.destinationProtocolVersion))))&&((this.sourceProtocolVersion == rhs.sourceProtocolVersion)||((this.sourceProtocolVersion!= null)&&this.sourceProtocolVersion.equals(rhs.sourceProtocolVersion))))&&((this.prefix == rhs.prefix)||((this.prefix!= null)&&this.prefix.equals(rhs.prefix))))&&((this.configuredAirbyteCatalog == rhs.configuredAirbyteCatalog)||((this.configuredAirbyteCatalog!= null)&&this.configuredAirbyteCatalog.equals(rhs.configuredAirbyteCatalog))))&&((this.isDestinationCustomConnector == rhs.isDestinationCustomConnector)||((this.isDestinationCustomConnector!= null)&&this.isDestinationCustomConnector.equals(rhs.isDestinationCustomConnector))))&&((this.namespaceDefinition == rhs.namespaceDefinition)||((this.namespaceDefinition!= null)&&this.namespaceDefinition.equals(rhs.namespaceDefinition))))&&((this.destinationDockerImage == rhs.destinationDockerImage)||((this.destinationDockerImage!= null)&&this.destinationDockerImage.equals(rhs.destinationDockerImage))))&&((this.resourceRequirements == rhs.resourceRequirements)||((this.resourceRequirements!= null)&&this.resourceRequirements.equals(rhs.resourceRequirements))))&&((this.isSourceCustomConnector == rhs.isSourceCustomConnector)||((this.isSourceCustomConnector!= null)&&this.isSourceCustomConnector.equals(rhs.isSourceCustomConnector))))&&((this.sourceResourceRequirements == rhs.sourceResourceRequirements)||((this.sourceResourceRequirements!= null)&&this.sourceResourceRequirements.equals(rhs.sourceResourceRequirements))))&&((this.namespaceFormat == rhs.namespaceFormat)||((this.namespaceFormat!= null)&&this.namespaceFormat.equals(rhs.namespaceFormat))))&&((this.sourceDockerImage == rhs.sourceDockerImage)||((this.sourceDockerImage!= null)&&this.sourceDockerImage.equals(rhs.sourceDockerImage))))&&((this.workspaceId == rhs.workspaceId)||((this.workspaceId!= null)&&this.workspaceId.equals(rhs.workspaceId))));
    }


    /**
     * Namespace Definition
     * <p>
     * Method used for computing final namespace in destination
     *
     */
    public enum NamespaceDefinitionType {

        SOURCE("source"),
        DESTINATION("destination"),
        CUSTOMFORMAT("customformat");
        private final String value;
        private final static Map<String, JobSyncConfig.NamespaceDefinitionType> CONSTANTS = new HashMap<String, JobSyncConfig.NamespaceDefinitionType>();

        static {
            for (JobSyncConfig.NamespaceDefinitionType c: values()) {
                CONSTANTS.put(c.value, c);
            }
        }

        private NamespaceDefinitionType(String value) {
            this.value = value;
        }

        @Override
        public String toString() {
            return this.value;
        }

        @JsonValue
        public String value() {
            return this.value;
        }

        @JsonCreator
        public static JobSyncConfig.NamespaceDefinitionType fromValue(String value) {
            JobSyncConfig.NamespaceDefinitionType constant = CONSTANTS.get(value);
            if (constant == null) {
                throw new IllegalArgumentException(value);
            } else {
                return constant;
            }
        }

    }

}
