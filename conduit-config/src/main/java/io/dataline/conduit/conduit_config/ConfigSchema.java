package io.dataline.conduit.conduit_config;

public enum ConfigSchema {
  SOURCE_CONNECTION_CONFIGURATION("SourceConnectionConfiguration.json"),
  STANDARD_CONNECTION_STATUS("StandardConnectionStatus.json"),
  STANDARD_DISCOVERY_OUTPUT("StandardDiscoveryOutput.json"),
  DESTINATION_CONNECTION_CONFIGURATION("DestinationConnectionConfiguration.json"),
  STANDARD_SYNC_CONFIGURATION("StandardSyncConfiguration.json"),
  STANDARD_SYNC_SUMMARY("StandardSyncSummary.json"),
  STANDARD_SYNC_STATE("StandardSyncState.json"),
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
