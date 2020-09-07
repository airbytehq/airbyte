package io.dataline.config.persistence;

import io.dataline.config.ConfigSchema;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncSchedule;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigRepository {

  private final static Logger LOGGER = LoggerFactory.getLogger(ConfigRepository.class);

  private final ConfigPersistence persistence;

  public ConfigRepository(ConfigPersistence persistence) {
    this.persistence = persistence;
  }

  public SourceConnectionImplementation getSourceConnectionImplementation(final UUID sourceImplementationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION,
        sourceImplementationId.toString(),
        SourceConnectionImplementation.class);
  }

  public DestinationConnectionImplementation getDestinationConnectionImplementation(final UUID destinationImplementationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.DESTINATION_CONNECTION_IMPLEMENTATION,
        destinationImplementationId.toString(),
        DestinationConnectionImplementation.class);
  }

  public StandardSync getStandardSync(final UUID connectionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.STANDARD_SYNC,
        connectionId.toString(),
        StandardSync.class);
  }

  public List<StandardSync> getStandardSyncs()
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return persistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class);
  }

  public StandardSyncSchedule getStandardSyncSchedule(final UUID connectionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(
        ConfigSchema.STANDARD_SYNC_SCHEDULE,
        connectionId.toString(),
        StandardSyncSchedule.class);
  }

}
