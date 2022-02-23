/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.migrate.MigrateConfig;
import io.airbyte.migrate.MigrationRunner;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RunMigration implements Runnable, AutoCloseable {

  private static final Logger LOGGER = LoggerFactory.getLogger(RunMigration.class);
  private final AirbyteVersion targetVersion;
  private final ConfigPersistence seedPersistence;
  private final ConfigDumpExporter configDumpExporter;
  private final ConfigDumpImporter configDumpImporter;
  private final List<File> filesToBeCleanedUp = new ArrayList<>();

  public RunMigration(final JobPersistence jobPersistence,
                      final ConfigRepository configRepository,
                      final AirbyteVersion targetVersion,
                      final ConfigPersistence seedPersistence,
                      final SpecFetcher specFetcher) {
    this.targetVersion = targetVersion;
    this.seedPersistence = seedPersistence;
    this.configDumpExporter = new ConfigDumpExporter(configRepository, jobPersistence, null);
    this.configDumpImporter = new ConfigDumpImporter(configRepository, jobPersistence, null, specFetcher, false);
  }

  @Override
  public void run() {
    try {
      // Export data
      final File exportData = configDumpExporter.dump();
      filesToBeCleanedUp.add(exportData);

      // Define output target
      final Path tempFolder = Files.createTempDirectory(Path.of("/tmp"), "airbyte_archive_output");
      final File output = Files.createTempFile(tempFolder, "airbyte_archive_output", ".tar.gz").toFile();
      filesToBeCleanedUp.add(output);
      filesToBeCleanedUp.add(tempFolder.toFile());

      // Run Migration
      final MigrateConfig migrateConfig = new MigrateConfig(exportData.toPath(), output.toPath(), targetVersion.serialize());
      MigrationRunner.run(migrateConfig);

      // Import data
      configDumpImporter.importDataWithSeed(targetVersion, output, seedPersistence);
    } catch (final IOException | JsonValidationException e) {
      throw new RuntimeException("Automatic migration failed", e);
    }
  }

  @Override
  public void close() throws IOException {
    for (final File file : filesToBeCleanedUp) {
      if (file.exists()) {
        LOGGER.info("Deleting " + file.getName());
        if (file.isDirectory()) {
          FileUtils.deleteDirectory(file);
        } else {
          Files.delete(file.toPath());
        }
      }
    }
  }

}
