package io.dataline.config;

public enum ConfigSchema {
  STANDARD_SOURCE("StandardSource.json"),
  SOURCE_CONNECTION_SPECIFICATION("SourceConnectionSpecification.json"),
  SOURCE_CONNECTION_IMPLEMENTATION("SourceConnectionImplementation.json"),
  STANDARD_CONNECTION_STATUS("StandardConnectionStatus.json"),
  STANDARD_DISCOVERY_OUTPUT("StandardDiscoveryOutput.json"),
  DESTINATION_CONNECTION_CONFIGURATION("DestinationConnectionConfiguration.json"),
  STANDARD_SYNC_CONFIGURATION("StandardSyncConfiguration.json"),
  STANDARD_SYNC_SUMMARY("StandardSyncSummary.json"),
  STANDARD_SYNC_STATE("StandardSyncState.json"),
  STANDARD_SYNC_SCHEDULE("StandardSyncSchedule.json"),
  STATE("State.json"),
  STANDARD_WORKSPACE_CONFIGURATION("StandardWorkspaceConfiguration.json");

  private final String schemaFilename;

  ConfigSchema(String schemaFilename) {
    this.schemaFilename = schemaFilename;
  }

  public String getSchemaFilename() {
    return schemaFilename;
  }
}
