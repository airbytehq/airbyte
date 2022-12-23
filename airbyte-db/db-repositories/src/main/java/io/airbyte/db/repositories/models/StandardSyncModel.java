/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.repositories.models;

import io.micronaut.core.annotation.NonNull;
import io.micronaut.data.annotation.GeneratedValue;
import io.micronaut.data.annotation.Id;
import io.micronaut.data.annotation.MappedEntity;

import javax.persistence.Entity;
import java.util.UUID;

//@MappedEntity
//@Entity(name="connection")
//public record StandardSyncModel(@NonNull @javax.persistence.Id @Id UUID id) {
//
//}

@MappedEntity
@Entity(name="connection")
public class StandardSyncModel {
    @NonNull
    public UUID getId() {
        return id;
    }

    public void setId(@NonNull UUID id) {
        this.id = id;
    }

    @NonNull
    public String getName() {
        return name;
    }

    public void setName(@NonNull String name) {
        this.name = name;
    }

    @GeneratedValue
    @NonNull @javax.persistence.Id @Id UUID id;
    @NonNull String name;

    public StandardSyncModel() {
    }

    public StandardSyncModel(@NonNull final UUID id, @NonNull final String name) {
        this.id = id;
        this.name = name;
    }

}
// @MappedEntity
// public class XStandardSyncModel {
//
// @Id
// @GeneratedValue
// private UUID id;
//
// public UUID getId() {
// return id;
// }
//
// public void setId(UUID id) {
// this.id = id;
// }
//
// /**
// * Namespace Definition
// * <p>
// * Method used for computing final namespace in destination
// * (Required)
// *
// */
// @JsonProperty("namespaceDefinition")
// @JsonPropertyDescription("Method used for computing final namespace in destination")
// private io.airbyte.config.JobSyncConfig.NamespaceDefinitionType namespaceDefinition =
// io.airbyte.config.JobSyncConfig.NamespaceDefinitionType.fromValue("source");
// @JsonProperty("namespaceFormat")
// private String namespaceFormat = null;
// /**
// * Prefix that will be prepended to the name of each stream when it is written to the destination.
// *
// */
// @JsonProperty("prefix")
// @JsonPropertyDescription("Prefix that will be prepended to the name of each stream when it is
// written to the destination.")
// private String prefix;
// /**
// *
// * (Required)
// *
// */
// @JsonProperty("sourceId")
// private UUID sourceId;
// /**
// *
// * (Required)
// *
// */
// @JsonProperty("destinationId")
// private UUID destinationId;
// @JsonProperty("operationIds")
// private List<UUID> operationIds = new ArrayList<UUID>();
// @JsonProperty("connectionId")
// private UUID connectionId;
// /**
// *
// * (Required)
// *
// */
// @JsonProperty("name")
// private String name;
// /**
// *
// * (Required)
// *
// */
// @JsonProperty("catalog")
// private ConfiguredAirbyteCatalog catalog;
// /**
// * A map of StreamDescriptor to an indicator of whether field selection is enabled for that
// stream.
// *
// */
// @JsonProperty("fieldSelectionData")
// @JsonPropertyDescription("A map of StreamDescriptor to an indicator of whether field selection is
// enabled for that stream.")
// private FieldSelectionData fieldSelectionData;
// @JsonProperty("status")
// private StandardSync.Status status;
// @JsonProperty("schedule")
// private Schedule schedule;
// /**
// *
// * (Required)
// *
// */
// @JsonProperty("manual")
// private Boolean manual;
// @JsonProperty("scheduleType")
// private StandardSync.ScheduleType scheduleType;
// @JsonProperty("scheduleData")
// private ScheduleData scheduleData;
// @JsonProperty("source_catalog_id")
// private UUID sourceCatalogId;
// /**
// * ResourceRequirements
// * <p>
// * generic configuration for pod source requirements
// *
// */
// @JsonProperty("resourceRequirements")
// @JsonPropertyDescription("generic configuration for pod source requirements")
// private ResourceRequirements resourceRequirements;
// /**
// * Geography
// * <p>
// * Geography Setting
// * (Required)
// *
// */
// @JsonProperty("geography")
// @JsonPropertyDescription("Geography Setting")
// private Geography geography;
// /**
// *
// * (Required)
// *
// */
// @JsonProperty("breakingChange")
// private Boolean breakingChange;
// @JsonProperty("notifySchemaChanges")
// private Boolean notifySchemaChanges;
// @JsonProperty("nonBreakingChangesPreference")
// private StandardSync.NonBreakingChangesPreference nonBreakingChangesPreference;
// private final static long serialVersionUID = -2077023533889992387L;

// }
