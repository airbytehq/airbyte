package io.dataline.config;

public enum ConfigSchema {
  // workspace
  STANDARD_WORKSPACE("StandardWorkspace.json"),

  // source
  STANDARD_SOURCE("StandardSource.json"),
  SOURCE_CONNECTION_SPECIFICATION("SourceConnectionSpecification.json"),
  SOURCE_CONNECTION_IMPLEMENTATION("SourceConnectionImplementation.json"),

  // destination
  STANDARD_DESTINATION("StandardDestination.json"),
  DESTINATION_CONNECTION_SPECIFICATION("DestinationConnectionSpecification.json"),
  DESTINATION_CONNECTION_IMPLEMENTATION("DestinationConnectionImplementation.json"),

  // test connection
  STANDARD_CONNECTION_STATUS("StandardConnectionStatus.json"),

  // discover schema
  STANDARD_DISCOVERY_OUTPUT("StandardDiscoveryOutput.json"),

  // sync
  STANDARD_SYNC("StandardSync.json"),
  STANDARD_SYNC_SUMMARY("StandardSyncSummary.json"),
  STANDARD_SYNC_SCHEDULE("StandardSyncSchedule.json"),
  STATE("State.json");

  private final String schemaFilename;

  ConfigSchema(String schemaFilename) {
    this.schemaFilename = schemaFilename;
  }

  public String getSchemaFilename() {
    return schemaFilename;
  }
}
