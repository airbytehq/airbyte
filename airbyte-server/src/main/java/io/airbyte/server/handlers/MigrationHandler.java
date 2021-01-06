package io.airbyte.server.handlers;

import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MigrationHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationHandler.class);

  private final ConfigRepository configRepository;
  private final JobPersistence jobPersistence;

  public MigrationHandler(final ConfigRepository configRepository, final JobPersistence jobPersistence) {
    this.configRepository = configRepository;
    this.jobPersistence = jobPersistence;
  }

  public Path exportData() {
    try {
      // Create temp folder where to export data
      final Path tempFolder = Files.createTempDirectory("airbyte_archive");
      exportAirbyteConfig(tempFolder);
      exportAirbyteDatabase(tempFolder);
      // TODO Add VERSION file
      // TODO Produce a tarball
      return Path.of("/tmp/archive.tar.gz");
    } catch (IOException e) {
      LOGGER.error("Export Data failed.");
      throw new RuntimeException(e);
    }
  }

  private void exportAirbyteConfig(Path outputFolder) {
    // TODO implement
  }

  private void exportAirbyteDatabase(Path outputFolder) {
    // TODO implement
  }

  public void importData(Path archive) {
    try {
      // Create temp folder where to extract archive
      final Path tempFolder = Files.createTempDirectory("airbyte_archive");
      // TODO Extract tarball to temp folder
      // TODO Check VERSION file
      importAirbyteConfig(tempFolder);
      importAirbyteDatabase(tempFolder);
    } catch (IOException e) {
      LOGGER.error("Import Data failed.");
      throw new RuntimeException(e);
    }
  }

  private void importAirbyteConfig(Path inputFolder) {
    // TODO implement
  }

  private void importAirbyteDatabase(Path inputFolder) {
    // TODO implement
  }

}
