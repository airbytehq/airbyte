/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.airbyte.api.model.generated.AirbyteCatalog;
import io.airbyte.api.model.generated.ConnectionSchedule;
import io.airbyte.api.model.generated.ConnectionStatus;
import io.airbyte.api.model.generated.NamespaceDefinitionType;
import io.airbyte.api.model.generated.ResourceRequirements;
import io.swagger.annotations.ApiModelProperty;
import java.util.List;
import java.util.Objects;
import java.util.UUID;
import javax.validation.Valid;
import javax.validation.constraints.NotNull;

public class ConnectionUpdate {

  private @Valid UUID connectionId;
  private @Valid NamespaceDefinitionType namespaceDefinition;
  private @Valid String namespaceFormat;
  private @Valid String name;
  private @Valid String prefix;
  private @Valid List<UUID> operationIds;
  private @Valid AirbyteCatalog syncCatalog;
  private @Valid ConnectionSchedule schedule;
  private @Valid ConnectionStatus status;
  private @Valid ResourceRequirements resourceRequirements;
  private @Valid UUID sourceCatalogId;

  /**
   **/
  public ConnectionUpdate connectionId(UUID connectionId) {
    this.connectionId = connectionId;
    return this;
  }

  @ApiModelProperty(required = true)
  @JsonProperty("connectionId")
  @NotNull
  public UUID getConnectionId() {
    return connectionId;
  }

  public void setConnectionId(UUID connectionId) {
    this.connectionId = connectionId;
  }

  /**
   **/
  public ConnectionUpdate namespaceDefinition(NamespaceDefinitionType namespaceDefinition) {
    this.namespaceDefinition = namespaceDefinition;
    return this;
  }

  @JsonProperty("namespaceDefinition")
  public NamespaceDefinitionType getNamespaceDefinition() {
    return namespaceDefinition;
  }

  public void setNamespaceDefinition(NamespaceDefinitionType namespaceDefinition) {
    this.namespaceDefinition = namespaceDefinition;
  }

  /**
   * Used when namespaceDefinition is &#39;customformat&#39;. If blank then behaves like
   * namespaceDefinition &#x3D; &#39;destination&#39;. If \&quot;${SOURCE_NAMESPACE}\&quot; then
   * behaves like namespaceDefinition &#x3D; &#39;source&#39;.
   **/
  public ConnectionUpdate namespaceFormat(String namespaceFormat) {
    this.namespaceFormat = namespaceFormat;
    return this;
  }

  @ApiModelProperty(example = "${SOURCE_NAMESPACE}",
                    value = "Used when namespaceDefinition is 'customformat'. If blank then behaves like namespaceDefinition = 'destination'. If \"${SOURCE_NAMESPACE}\" then behaves like namespaceDefinition = 'source'.")
  @JsonProperty("namespaceFormat")
  public String getNamespaceFormat() {
    return namespaceFormat;
  }

  public void setNamespaceFormat(String namespaceFormat) {
    this.namespaceFormat = namespaceFormat;
  }

  /**
   * Name that will be set to this connection
   **/
  public ConnectionUpdate name(String name) {
    this.name = name;
    return this;
  }

  @ApiModelProperty("Name that will be set to this connection")
  @JsonProperty("name")
  public String getName() {
    return name;
  }

  public void setName(String name) {
    this.name = name;
  }

  /**
   * Prefix that will be prepended to the name of each stream when it is written to the destination.
   **/
  public ConnectionUpdate prefix(String prefix) {
    this.prefix = prefix;
    return this;
  }

  @ApiModelProperty("Prefix that will be prepended to the name of each stream when it is written to the destination.")
  @JsonProperty("prefix")
  public String getPrefix() {
    return prefix;
  }

  public void setPrefix(String prefix) {
    this.prefix = prefix;
  }

  /**
   **/
  public ConnectionUpdate operationIds(List<UUID> operationIds) {
    this.operationIds = operationIds;
    return this;
  }

  @JsonProperty("operationIds")
  public List<UUID> getOperationIds() {
    return operationIds;
  }

  public void setOperationIds(List<UUID> operationIds) {
    this.operationIds = operationIds;
  }

  /**
   **/
  public ConnectionUpdate syncCatalog(AirbyteCatalog syncCatalog) {
    this.syncCatalog = syncCatalog;
    return this;
  }

  @JsonProperty("syncCatalog")
  public AirbyteCatalog getSyncCatalog() {
    return syncCatalog;
  }

  public void setSyncCatalog(AirbyteCatalog syncCatalog) {
    this.syncCatalog = syncCatalog;
  }

  /**
   **/
  public ConnectionUpdate schedule(ConnectionSchedule schedule) {
    this.schedule = schedule;
    return this;
  }

  @JsonProperty("schedule")
  public ConnectionSchedule getSchedule() {
    return schedule;
  }

  public void setSchedule(ConnectionSchedule schedule) {
    this.schedule = schedule;
  }

  /**
   **/
  public ConnectionUpdate status(ConnectionStatus status) {
    this.status = status;
    return this;
  }

  @JsonProperty("status")
  public ConnectionStatus getStatus() {
    return status;
  }

  public void setStatus(ConnectionStatus status) {
    this.status = status;
  }

  /**
   **/
  public ConnectionUpdate resourceRequirements(ResourceRequirements resourceRequirements) {
    this.resourceRequirements = resourceRequirements;
    return this;
  }

  @JsonProperty("resourceRequirements")
  public ResourceRequirements getResourceRequirements() {
    return resourceRequirements;
  }

  public void setResourceRequirements(ResourceRequirements resourceRequirements) {
    this.resourceRequirements = resourceRequirements;
  }

  /**
   **/
  public ConnectionUpdate sourceCatalogId(UUID sourceCatalogId) {
    this.sourceCatalogId = sourceCatalogId;
    return this;
  }

  @JsonProperty("sourceCatalogId")
  public UUID getSourceCatalogId() {
    return sourceCatalogId;
  }

  public void setSourceCatalogId(UUID sourceCatalogId) {
    this.sourceCatalogId = sourceCatalogId;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    ConnectionUpdate connectionUpdate = (ConnectionUpdate) o;
    return Objects.equals(this.connectionId, connectionUpdate.connectionId) &&
        Objects.equals(this.namespaceDefinition, connectionUpdate.namespaceDefinition) &&
        Objects.equals(this.namespaceFormat, connectionUpdate.namespaceFormat) &&
        Objects.equals(this.name, connectionUpdate.name) &&
        Objects.equals(this.prefix, connectionUpdate.prefix) &&
        Objects.equals(this.operationIds, connectionUpdate.operationIds) &&
        Objects.equals(this.syncCatalog, connectionUpdate.syncCatalog) &&
        Objects.equals(this.schedule, connectionUpdate.schedule) &&
        Objects.equals(this.status, connectionUpdate.status) &&
        Objects.equals(this.resourceRequirements, connectionUpdate.resourceRequirements) &&
        Objects.equals(this.sourceCatalogId, connectionUpdate.sourceCatalogId);
  }

  @Override
  public int hashCode() {
    return Objects.hash(connectionId, namespaceDefinition, namespaceFormat, name, prefix, operationIds, syncCatalog, schedule, status,
        resourceRequirements, sourceCatalogId);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder();
    sb.append("class ConnectionUpdate {\n");

    sb.append("    connectionId: ").append(toIndentedString(connectionId)).append("\n");
    sb.append("    namespaceDefinition: ").append(toIndentedString(namespaceDefinition)).append("\n");
    sb.append("    namespaceFormat: ").append(toIndentedString(namespaceFormat)).append("\n");
    sb.append("    name: ").append(toIndentedString(name)).append("\n");
    sb.append("    prefix: ").append(toIndentedString(prefix)).append("\n");
    sb.append("    operationIds: ").append(toIndentedString(operationIds)).append("\n");
    sb.append("    syncCatalog: ").append(toIndentedString(syncCatalog)).append("\n");
    sb.append("    schedule: ").append(toIndentedString(schedule)).append("\n");
    sb.append("    status: ").append(toIndentedString(status)).append("\n");
    sb.append("    resourceRequirements: ").append(toIndentedString(resourceRequirements)).append("\n");
    sb.append("    sourceCatalogId: ").append(toIndentedString(sourceCatalogId)).append("\n");
    sb.append("}");
    return sb.toString();
  }

  /**
   * Convert the given object to string with each line indented by 4 spaces (except the first line).
   */
  private String toIndentedString(Object o) {
    if (o == null) {
      return "null";
    }
    return o.toString().replace("\n", "\n    ");
  }

}
