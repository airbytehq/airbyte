package io.airbyte.db.repositories.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;

import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;

import java.util.UUID;

@Entity
public class StandardSyncModel {
    @Id
    @GeneratedValue
    private UUID connectionId;
//
//    /**
//     * Namespace Definition
//     * <p>
//     * Method used for computing final namespace in destination
//     * (Required)
//     *
//     */
//    @JsonProperty("namespaceDefinition")
//    @JsonPropertyDescription("Method used for computing final namespace in destination")
//    private io.airbyte.config.JobSyncConfig.NamespaceDefinitionType namespaceDefinition = io.airbyte.config.JobSyncConfig.NamespaceDefinitionType.fromValue("source");
//    @JsonProperty("namespaceFormat")
//    private String namespaceFormat = null;
//    /**
//     * Prefix that will be prepended to the name of each stream when it is written to the destination.
//     *
//     */
//    @JsonProperty("prefix")
//    @JsonPropertyDescription("Prefix that will be prepended to the name of each stream when it is written to the destination.")
//    private String prefix;
//    /**
//     *
//     * (Required)
//     *
//     */
//    @JsonProperty("sourceId")
//    private UUID sourceId;
//    /**
//     *
//     * (Required)
//     *
//     */
//    @JsonProperty("destinationId")
//    private UUID destinationId;
//    @JsonProperty("operationIds")
//    private List<UUID> operationIds = new ArrayList<UUID>();
//    @JsonProperty("connectionId")
//    private UUID connectionId;
//    /**
//     *
//     * (Required)
//     *
//     */
//    @JsonProperty("name")
//    private String name;
//    /**
//     *
//     * (Required)
//     *
//     */
//    @JsonProperty("catalog")
//    private ConfiguredAirbyteCatalog catalog;
//    /**
//     * A map of StreamDescriptor to an indicator of whether field selection is enabled for that stream.
//     *
//     */
//    @JsonProperty("fieldSelectionData")
//    @JsonPropertyDescription("A map of StreamDescriptor to an indicator of whether field selection is enabled for that stream.")
//    private FieldSelectionData fieldSelectionData;
//    @JsonProperty("status")
//    private StandardSync.Status status;
//    @JsonProperty("schedule")
//    private Schedule schedule;
//    /**
//     *
//     * (Required)
//     *
//     */
//    @JsonProperty("manual")
//    private Boolean manual;
//    @JsonProperty("scheduleType")
//    private StandardSync.ScheduleType scheduleType;
//    @JsonProperty("scheduleData")
//    private ScheduleData scheduleData;
//    @JsonProperty("source_catalog_id")
//    private UUID sourceCatalogId;
//    /**
//     * ResourceRequirements
//     * <p>
//     * generic configuration for pod source requirements
//     *
//     */
//    @JsonProperty("resourceRequirements")
//    @JsonPropertyDescription("generic configuration for pod source requirements")
//    private ResourceRequirements resourceRequirements;
//    /**
//     * Geography
//     * <p>
//     * Geography Setting
//     * (Required)
//     *
//     */
//    @JsonProperty("geography")
//    @JsonPropertyDescription("Geography Setting")
//    private Geography geography;
//    /**
//     *
//     * (Required)
//     *
//     */
//    @JsonProperty("breakingChange")
//    private Boolean breakingChange;
//    @JsonProperty("notifySchemaChanges")
//    private Boolean notifySchemaChanges;
//    @JsonProperty("nonBreakingChangesPreference")
//    private StandardSync.NonBreakingChangesPreference nonBreakingChangesPreference;
//    private final static long serialVersionUID = -2077023533889992387L;

}
