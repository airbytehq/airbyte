/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.commons.set.MoreSets;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.io.FileUtils;
import org.apache.logging.log4j.util.Strings;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Migrate {

  private static final Logger LOGGER = LoggerFactory.getLogger(Migrate.class);

  public static final String VERSION_FILE_NAME = "VERSION";

  private final Path migrateRoot;
  private final JsonSchemaValidator jsonSchemaValidator;
  private final List<Migration> migrations;

  public Migrate(Path migrateRoot) {
    this(migrateRoot, Migrations.MIGRATIONS);
  }

  public Migrate(Path migrateRoot, List<Migration> migrations) {
    this.migrateRoot = migrateRoot;
    this.jsonSchemaValidator = new JsonSchemaValidator();
    this.migrations = migrations;
  }

  public void run(MigrateConfig migrateConfig) throws IOException {
    // ensure migration root exists
    Files.createDirectories(migrateRoot);
    final Path initialInputPath = migrateConfig.getInputPath();
    // detect current version.
    final String currentVersion = getCurrentVersion(initialInputPath);
    // detect desired version.
    final String targetVersion = migrateConfig.getTargetVersion();
    Preconditions.checkArgument(!currentVersion.equals("dev"), "Cannot migrate data with version dev.");
    Preconditions.checkArgument(targetVersion == null || !targetVersion.equals("dev"), "Cannot migrate data to version dev.");

    LOGGER.info("Starting migrations. Current version: {}, Target version: {}", currentVersion, targetVersion);

    // select migrations to run.
    final List<AirbyteVersion> migrationVersions = migrations.stream().map(m -> new AirbyteVersion(m.getVersion())).collect(Collectors.toList());
    final int currentVersionIndex = getPreviousMigration(migrationVersions, new AirbyteVersion(currentVersion));
    Preconditions.checkArgument(currentVersionIndex >= 0, "No migration found for current version: " + currentVersion);
    final int targetVersionIndex;
    if (Strings.isNotEmpty(targetVersion)) {
      targetVersionIndex = migrations.stream().map(Migration::getVersion).collect(Collectors.toList()).indexOf(targetVersion);
    } else {
      targetVersionIndex = migrations.size() - 1;
    }

    Preconditions.checkArgument(targetVersionIndex >= 0, "No migration found for target version: " + targetVersion);
    Preconditions.checkArgument(currentVersionIndex < targetVersionIndex, String.format(
        "Target version is not greater than the current version. current version: %s, target version: %s. Note migration order is determined by membership in migrations list, not any canonical sorting of the version string itself.",
        currentVersion, targetVersion));

    // for each migration to run:
    Path inputPath = initialInputPath;
    for (int i = currentVersionIndex + 1; i <= targetVersionIndex; i++) {
      // run migration
      // write output of each migration to disk.
      final Migration migration = migrations.get(i);
      LOGGER.info("Migrating from version: {} to version {}.", migrations.get(i - 1).getVersion(), migration.getVersion());
      final Path outputPath = runMigration(migration, inputPath);
      IOs.writeFile(outputPath.resolve(VERSION_FILE_NAME), migration.getVersion());
      inputPath = outputPath;
    }

    // write final output
    FileUtils.deleteDirectory(migrateConfig.getOutputPath().toFile());
    Files.createDirectories(migrateConfig.getOutputPath());
    FileUtils.copyDirectory(inputPath.toFile(), migrateConfig.getOutputPath().toFile());

    LOGGER.info("Migrations complete. Now on version: {}", targetVersion);
  }

  private Path runMigration(Migration migration, Path migrationInputRoot) throws IOException {
    final Path tmpOutputDir = Files.createDirectories(migrateRoot.resolve(migration.getVersion()));

    // create a map of each input resource path to the input stream.
    final Map<ResourceId, AutoCloseableIterator<JsonNode>> inputData = createInputStreams(migration, migrationInputRoot);
    final Map<ResourceId, Stream<JsonNode>> inputDataStreams = inputData.entrySet().stream()
        .collect(Collectors.toMap(
            Map.Entry::getKey,
            entry -> MoreStreams.toStream(entry.getValue())
                .peek(r -> {
                  try {
                    jsonSchemaValidator.ensure(migration.getInputSchema().get(entry.getKey()), r);
                  } catch (JsonValidationException e) {
                    throw new IllegalArgumentException(
                        String.format("Input data schema does not match declared input schema %s.", entry.getKey().getName()), e);
                  }
                })));

    final Map<ResourceId, RecordConsumer> outputStreams = createOutputStreams(migration, tmpOutputDir);
    // make the java compiler happy (it can't resolve that RecordConsumer is, in fact, a
    // Consumer<JsonNode>).
    final Map<ResourceId, Consumer<JsonNode>> outputDataWithGenericType = MigrationUtils.mapRecordConsumerToConsumer(outputStreams);

    // do the migration.
    new MigrateWithMetadata(migration).migrate(inputDataStreams, outputDataWithGenericType);

    // clean up.
    inputData.values().forEach(v -> Exceptions.toRuntime(v::close));
    outputStreams.values().forEach(v -> Exceptions.toRuntime(v::close));

    return tmpOutputDir;
  }

  private Map<ResourceId, AutoCloseableIterator<JsonNode>> createInputStreams(Migration migration, Path migrationInputRoot) {
    final Map<ResourceId, AutoCloseableIterator<JsonNode>> resourceIdToInputStreams = MoreMaps.merge(
        createInputStreamsForResourceType(migrationInputRoot, ResourceType.CONFIG),
        createInputStreamsForResourceType(migrationInputRoot, ResourceType.JOB));

    System.out.println("\n\nschema = \n" + migration.getInputSchema().keySet().stream().map(ResourceId::getName).collect(Collectors.joining("\n")));
    System.out.println("\n\nrecords = \n" + resourceIdToInputStreams.keySet().stream().map(ResourceId::getName).collect(Collectors.joining("\n")));
    if (!migration.getInputSchema().keySet().containsAll(resourceIdToInputStreams.keySet())) {
      try {
        // we know something is wrong. check equality to get a full log message of the total difference.
        MoreSets.assertEqualsVerbose(migration.getInputSchema().keySet(), resourceIdToInputStreams.keySet());
      } catch (IllegalArgumentException e) {
        throw new IllegalArgumentException("Input records contain resource not declared in schema resources", e);
      }
    }
    return resourceIdToInputStreams;
  }

  private Map<ResourceId, AutoCloseableIterator<JsonNode>> createInputStreamsForResourceType(Path migrationInputRoot, ResourceType resourceType) {
    final List<Path> inputFilePaths = FileUtils.listFiles(migrationInputRoot.resolve(resourceType.getDirectoryName()).toFile(), null, false)
        .stream()
        .map(File::toPath)
        .collect(Collectors.toList());

    final Map<ResourceId, AutoCloseableIterator<JsonNode>> inputData = new HashMap<>();
    for (final Path absolutePath : inputFilePaths) {
      final ResourceId resourceId = ResourceId.fromRecordFilePath(resourceType, absolutePath);
      AutoCloseableIterator<JsonNode> recordInputStream = Yamls.deserializeArray(IOs.inputStream(absolutePath));
      inputData.put(resourceId, recordInputStream);
    }

    return inputData;
  }

  private Map<ResourceId, RecordConsumer> createOutputStreams(Migration migration, Path outputDir) throws IOException {
    final Map<ResourceId, RecordConsumer> pathToOutputStream = new HashMap<>();

    for (Map.Entry<ResourceId, JsonNode> entry : migration.getOutputSchema().entrySet()) {
      final ResourceId resourceId = entry.getKey();
      final JsonNode schema = entry.getValue();
      final Path absolutePath = outputDir.resolve(resourceId.getResourceRelativePath());
      Files.createDirectories(absolutePath.getParent());
      Files.createFile(absolutePath);
      final BufferedWriter recordOutputWriter = new BufferedWriter(new FileWriter(absolutePath.toFile()));
      final RecordConsumer recordConsumer = new RecordConsumer(recordOutputWriter, jsonSchemaValidator, schema);
      pathToOutputStream.put(resourceId, recordConsumer);
    }

    return pathToOutputStream;
  }

  private static String getCurrentVersion(Path path) {
    return IOs.readFile(path.resolve(VERSION_FILE_NAME)).trim();
  }

  @VisibleForTesting
  static int getPreviousMigration(List<AirbyteVersion> migrationVersions, AirbyteVersion currentVersion) {
    for (int i = 0; i < migrationVersions.size(); i++) {
      final AirbyteVersion migrationVersion = migrationVersions.get(i);
      if (migrationVersion.patchVersionCompareTo(currentVersion) == 0) {
        return i;
      }
      if (migrationVersions.size() > i + 1) {
        final AirbyteVersion nextVersion = migrationVersions.get(i + 1);
        if (nextVersion.patchVersionCompareTo(currentVersion) > 0) {
          return i;
        }
      }
    }
    return -1;
  }

}
