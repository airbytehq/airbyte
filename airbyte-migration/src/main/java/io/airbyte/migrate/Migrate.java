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
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.migrate.migrations.MigrationV0_11_0;
import io.airbyte.migrate.migrations.MigrationV0_11_1;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
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

  private static final String VERSION_FILE_NAME = "VERSION";

  private static final List<Migration> MIGRATIONS = ImmutableList.of(
      new MigrationV0_11_0(),
      new MigrationV0_11_1());

  private final Path workspaceRoot;
  private final JsonSchemaValidator jsonSchemaValidator;

  public Migrate(Path workspaceRoot) {
    this(workspaceRoot, new JsonSchemaValidator());
  }

  public Migrate(Path workspaceRoot, JsonSchemaValidator jsonSchemaValidator) {
    this.workspaceRoot = workspaceRoot;
    this.jsonSchemaValidator = jsonSchemaValidator;
  }

  public void run(MigrateConfig migrateConfig) throws IOException {
    final Path initialInputPath = migrateConfig.getInputPath();
    // detect current version.
    final String currentVersion = getCurrentVersion(initialInputPath);
    // detect desired version.
    final String targetVersion = migrateConfig.getTargetVersion();
    // select migrations to run.
    final int currentVersionIndex = MIGRATIONS.stream().map(Migration::getVersion).collect(Collectors.toList()).indexOf(currentVersion);
    Preconditions.checkState(currentVersionIndex >= 0, "No migration found for current version: " + currentVersion);
    final int targetVersionIndex = MIGRATIONS.stream().map(Migration::getVersion).collect(Collectors.toList()).indexOf(targetVersion);
    Preconditions.checkState(targetVersionIndex >= 0, "No migration found for target version: " + targetVersion);
    Preconditions.checkState(currentVersionIndex < targetVersionIndex, String
        .format("Target version is not greater than the current version. current version: %s, target version: %s", currentVersion, targetVersion));

    // for each migration to run:
    Path inputPath = initialInputPath;
    for (int i = currentVersionIndex + 1; i == targetVersionIndex; i++) {
      // run migration
      // write output of each migration to disk.
      final Migration migration = MIGRATIONS.get(i);
      final Path outputPath = runMigration(migration, inputPath);
      IOs.writeFile(outputPath.resolve(VERSION_FILE_NAME), migration.getVersion());
      inputPath = outputPath;
    }

    // write final output
    FileUtils.deleteDirectory(migrateConfig.getOutputPath().toFile());
    Files.createDirectories(migrateConfig.getOutputPath());
    IOs.copyDir(inputPath, migrateConfig.getOutputPath());
  }

  private Path runMigration(Migration migration, Path inputPath) throws IOException {
    final Path outputDir = Files.createDirectory(workspaceRoot.resolve(migration.getVersion()));

    final Map<Path, Stream<JsonNode>> inputData = new HashMap<>();
    final Map<Path, RecordConsumer> outputData = new HashMap<>();

    final List<Path> inputFilePaths = new ArrayList<>();
    inputFilePaths.addAll(IOs.listFiles(inputPath.resolve("config")));
    // inputFilePaths.addAll(IOs.listFiles(inputPath.resolve("jobs")));

    // todo use map instead.
    for (final Path absolutePath : inputFilePaths) {
      final Path relativePath = inputPath.relativize(absolutePath);
      // final String keyName =
      // com.google.common.io.Files.getNameWithoutExtension(path.getFileName().toString());
      if (!migration.getInputSchema().containsKey(relativePath)) {
        throw new IllegalArgumentException(
            String.format("Input data contains resource not declared in migration. resource: %s, declared resources: %s", relativePath,
                migration.getInputSchema().keySet()));
      }

      final Stream<JsonNode> recordInputStream = Files.lines(absolutePath)
          .map(Jsons::deserialize)
          .peek(r -> Exceptions.toRuntime(() -> jsonSchemaValidator.ensure(r, migration.getInputSchema().get(relativePath))));
      inputData.put(relativePath, recordInputStream);
    }

    for (Map.Entry<Path, JsonNode> entry : migration.getOutputSchema().entrySet()) {
      final Path path = entry.getKey();
      final Path absolutePath = outputDir.resolve(entry.getKey());
      Files.createDirectories(absolutePath.getParent());
      Files.createFile(absolutePath);
      final BufferedWriter recordOutputWriter = new BufferedWriter(new FileWriter(absolutePath.toFile()));
      final RecordConsumer recordConsumer = new RecordConsumer(recordOutputWriter, jsonSchemaValidator, migration.getOutputSchema().get(path));
      outputData.put(path, recordConsumer);
    }

    // make the java compiler happy.
    final Map<Path, Consumer<JsonNode>> outputDataWithGenericType = outputData.entrySet()
        .stream()
        .collect(Collectors.toMap(Entry::getKey, e -> (v) -> e.getValue().accept(v)));
    migration.migrate(inputData, outputDataWithGenericType);

    inputData.values().forEach(BaseStream::close);
    outputData.values().forEach(v -> Exceptions.toRuntime(v::close));

    return outputDir;
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

  private static class MigrateConfig {

    private final Path inputPath;
    private final Path outputPath;
    private final String targetVersion;

    public MigrateConfig(Path inputPath, Path outputPath, String targetVersion) {
      this.inputPath = inputPath;
      this.outputPath = outputPath;
      this.targetVersion = targetVersion;
    }

    public Path getInputPath() {
      return inputPath;
    }

    public Path getOutputPath() {
      return outputPath;
    }

    public String getTargetVersion() {
      return targetVersion;
    }

  }

}
