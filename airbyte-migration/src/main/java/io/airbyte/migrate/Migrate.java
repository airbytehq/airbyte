/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableList;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.commons.set.MoreSets;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.migrate.migrations.MigrationV0_11_0;
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
import java.util.Map.Entry;
import java.util.function.Consumer;
import java.util.stream.BaseStream;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;
import org.apache.commons.io.FileUtils;

public class Migrate {

  public static final String VERSION_FILE_NAME = "VERSION";

  // all migrations must be added to the list in the order that they should be applied.
  private static final List<Migration> MIGRATIONS = ImmutableList.of(new MigrationV0_11_0());

  private final Path migrateRoot;
  private final JsonSchemaValidator jsonSchemaValidator;
  private final List<Migration> migrations;

  public Migrate(Path migrateRoot) {
    this(migrateRoot, MIGRATIONS);
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
    // select migrations to run.
    final int currentVersionIndex = migrations.stream().map(Migration::getVersion).collect(Collectors.toList()).indexOf(currentVersion);
    Preconditions.checkArgument(currentVersionIndex >= 0, "No migration found for current version: " + currentVersion);
    final int targetVersionIndex = migrations.stream().map(Migration::getVersion).collect(Collectors.toList()).indexOf(targetVersion);
    Preconditions.checkArgument(targetVersionIndex >= 0, "No migration found for target version: " + targetVersion);
    Preconditions.checkArgument(currentVersionIndex < targetVersionIndex, String
        .format(
            "Target version is not greater than the current version. current version: %s, target version: %s. Note migration order is determined by membership in migrations list, not any canonical sorting of the version string itself.",
            currentVersion, targetVersion));

    // for each migration to run:
    Path inputPath = initialInputPath;
    for (int i = currentVersionIndex + 1; i <= targetVersionIndex; i++) {
      // run migration
      // write output of each migration to disk.
      final Migration migration = migrations.get(i);
      final Path outputPath = runMigration(migration, inputPath);
      IOs.writeFile(outputPath.resolve(VERSION_FILE_NAME), migration.getVersion());
      inputPath = outputPath;
    }

    // write final output
    FileUtils.deleteDirectory(migrateConfig.getOutputPath().toFile());
    Files.createDirectories(migrateConfig.getOutputPath());
    FileUtils.copyDirectory(inputPath.toFile(), migrateConfig.getOutputPath().toFile());
  }

  private Path runMigration(Migration migration, Path migrationInputRoot) throws IOException {
    final Path tmpOutputDir = Files.createDirectories(migrateRoot.resolve(migration.getVersion()));

    // create a map of each input resource path to the input stream.
    final Map<ResourceId, Stream<JsonNode>> inputData = createInputStreams(migration, migrationInputRoot);

    final Map<ResourceId, RecordConsumer> outputStreams = createOutputStreams(migration, tmpOutputDir);
    // make the java compiler happy (it can't resolve that RecordConsumer is, in fact, a
    // Consumer<JsonNode>).
    final Map<ResourceId, Consumer<JsonNode>> outputDataWithGenericType = mapRecordConsumerToConsumer(outputStreams);

    // do the migration.
    migration.migrate(inputData, outputDataWithGenericType);

    // clean up.
    inputData.values().forEach(BaseStream::close);
    outputStreams.values().forEach(v -> Exceptions.toRuntime(v::close));

    return tmpOutputDir;
  }

  private Map<ResourceId, Stream<JsonNode>> createInputStreams(Migration migration, Path migrationInputRoot) {
    final Map<ResourceId, Stream<JsonNode>> resourceIdToInputStreams = MoreMaps.merge(
        createInputStreamsForResourceType(migration, migrationInputRoot, ResourceType.CONFIG),
        createInputStreamsForResourceType(migration, migrationInputRoot, ResourceType.JOB));

    try {
      MoreSets.assertEqualsVerbose(migration.getInputSchema().keySet(), resourceIdToInputStreams.keySet());
    } catch (IllegalArgumentException e) {
      throw new IllegalArgumentException("Input record resources do not match declared schema resources", e);
    }
    return resourceIdToInputStreams;
  }

  private Map<ResourceId, Stream<JsonNode>> createInputStreamsForResourceType(Migration migration,
                                                                              Path migrationInputRoot,
                                                                              ResourceType resourceType) {
    final List<Path> inputFilePaths = FileUtils.listFiles(migrationInputRoot.resolve(resourceType.getDirectoryName()).toFile(), null, false)
        .stream()
        .map(File::toPath)
        .collect(Collectors.toList());

    final Map<ResourceId, Stream<JsonNode>> inputData = new HashMap<>();
    for (final Path absolutePath : inputFilePaths) {
      final ResourceId resourceId = ResourceId.fromRecordFilePath(resourceType, absolutePath);
      final Stream<JsonNode> recordInputStream = MoreStreams.toStream(Yamls.deserialize(IOs.readFile(absolutePath)).elements())
          .peek(r -> {
            try {
              jsonSchemaValidator.ensure(migration.getInputSchema().get(resourceId), r);
            } catch (JsonValidationException e) {
              throw new IllegalArgumentException("Input data schema does not match declared input schema.", e);
            }
          });
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

  private static Map<ResourceId, Consumer<JsonNode>> mapRecordConsumerToConsumer(Map<ResourceId, RecordConsumer> recordConsumers) {
    return recordConsumers.entrySet()
        .stream()
        .collect(Collectors.toMap(Entry::getKey, e -> (v) -> e.getValue().accept(v)));
  }

  private static String getCurrentVersion(Path path) {
    return IOs.readFile(path.resolve(VERSION_FILE_NAME)).trim();
  }

  private static MigrateConfig parse(String[] args) {
    final ArgumentParser parser = ArgumentParsers.newFor(Migrate.class.getName()).build()
        .defaultHelp(true)
        .description("Migrate Airbyte Data");

    parser.addArgument("--input")
        .required(true)
        .help("Path to data to migrate.");

    parser.addArgument("--output")
        .required(true)
        .help("Path to where to output migrated data.");

    parser.addArgument("--target-version")
        .required(true)
        .help("Version to upgrade the data to");

    try {
      final Namespace parsed = parser.parseArgs(args);
      final Path inputPath = Path.of(parsed.getString("input"));
      final Path outputPath = Path.of(parsed.getString("output"));
      final String targetVersion = parsed.getString("target_version");
      return new MigrateConfig(inputPath, outputPath, targetVersion);
    } catch (ArgumentParserException e) {
      parser.handleError(e);
      throw new IllegalArgumentException(e);
    }
  }

  public static void main(String[] args) throws IOException {
    final MigrateConfig migrateConfig = parse(args);
    final Path workspaceRoot = Files.createTempDirectory(Path.of("/tmp"), "migrate");
    new Migrate(workspaceRoot).run(migrateConfig);
  }

}
