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

package io.airbyte.db.instance.development;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.db.instance.FlywayDatabaseMigrator;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;
import org.flywaydb.core.api.ClassProvider;
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.MigrationVersion;
import org.flywaydb.core.api.configuration.Configuration;
import org.flywaydb.core.api.migration.JavaMigration;
import org.flywaydb.core.api.output.MigrateResult;
import org.flywaydb.core.api.resolver.ResolvedMigration;
import org.flywaydb.core.internal.resolver.java.ScanningJavaMigrationResolver;
import org.flywaydb.core.internal.scanner.LocationScannerCache;
import org.flywaydb.core.internal.scanner.ResourceNameCache;
import org.flywaydb.core.internal.scanner.Scanner;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MigrationDevHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationDevHelper.class);

  /**
   * This method is used for migration development. Run it to see how your migration changes the
   * database schema.
   */
  public static void runLastMigration(DevDatabaseMigrator migrator) throws IOException {
    migrator.createBaseline();

    List<MigrationInfo> preMigrationInfoList = migrator.list();
    System.out.println("\n==== Pre Migration Info ====\n" + FlywayFormatter.formatMigrationInfoList(preMigrationInfoList));
    System.out.println("\n==== Pre Migration Schema ====\n" + migrator.dumpSchema() + "\n");

    MigrateResult migrateResult = migrator.migrate();
    System.out.println("\n==== Migration Result ====\n" + FlywayFormatter.formatMigrationResult(migrateResult));

    List<MigrationInfo> postMigrationInfoList = migrator.list();
    System.out.println("\n==== Post Migration Info ====\n" + FlywayFormatter.formatMigrationInfoList(postMigrationInfoList));
    System.out.println("\n==== Post Migration Schema ====\n" + migrator.dumpSchema() + "\n");
  }

  public static void createNextMigrationFile(String dbIdentifier, FlywayDatabaseMigrator migrator) throws IOException {
    String description = "New_migration";

    MigrationVersion nextMigrationVersion = getNextMigrationVersion(migrator);
    String versionId = nextMigrationVersion.toString().replaceAll("\\.", "_");

    String template = MoreResources.readResource("migration_template.txt");
    String newMigration = template.replace("<db-name>", dbIdentifier)
        .replace("<version-id>", versionId)
        .replace("<description>", description)
        .strip();

    String fileName = String.format("V%s__%s.java", versionId, description);
    String filePath = String.format("src/main/java/io/airbyte/db/instance/%s/migrations/%s", dbIdentifier, fileName);

    LOGGER.info("New migration file: {}", filePath);

    File file = new File(Path.of(filePath).toUri());
    FileUtils.forceMkdirParent(file);

    try (PrintWriter writer = new PrintWriter(file)) {
      writer.println(newMigration);
    } catch (FileNotFoundException e) {
      throw new IOException(e);
    }
  }

  public static Optional<MigrationVersion> getSecondToLastMigrationVersion(FlywayDatabaseMigrator migrator) {
    List<ResolvedMigration> migrations = getAllMigrations(migrator);
    if (migrations.isEmpty() || migrations.size() == 1) {
      return Optional.empty();
    }
    return Optional.of(migrations.get(migrations.size() - 2).getVersion());
  }

  /**
   * This method is for migration development and testing purposes. So it is not exposed on the
   * interface. Reference:
   * https://github.com/flyway/flyway/blob/master/flyway-core/src/main/java/org/flywaydb/core/Flyway.java#L621.
   */
  private static List<ResolvedMigration> getAllMigrations(FlywayDatabaseMigrator migrator) {
    Configuration configuration = migrator.getFlyway().getConfiguration();
    ClassProvider<JavaMigration> scanner = new Scanner<>(
        JavaMigration.class,
        Arrays.asList(configuration.getLocations()),
        configuration.getClassLoader(),
        configuration.getEncoding(),
        configuration.getDetectEncoding(),
        false,
        new ResourceNameCache(),
        new LocationScannerCache(),
        configuration.getFailOnMissingLocations());
    ScanningJavaMigrationResolver resolver = new ScanningJavaMigrationResolver(scanner, configuration);
    return resolver.resolveMigrations(() -> configuration).stream()
        // There may be duplicated migration from the resolver.
        .distinct()
        .collect(Collectors.toList());
  }

  private static Optional<MigrationVersion> getLastMigrationVersion(FlywayDatabaseMigrator migrator) {
    List<ResolvedMigration> migrations = getAllMigrations(migrator);
    if (migrations.isEmpty()) {
      return Optional.empty();
    }
    return Optional.of(migrations.get(migrations.size() - 1).getVersion());
  }

  @VisibleForTesting
  static AirbyteVersion getCurrentAirbyteVersion() {
    try (BufferedReader reader = new BufferedReader(new FileReader("../.env"))) {
      String line;
      while ((line = reader.readLine()) != null) {
        if (line.startsWith("VERSION")) {
          return new AirbyteVersion(line.split("=")[1]);
        }
      }
    } catch (FileNotFoundException e) {
      throw new IllegalStateException("Cannot find the .env file");
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    throw new IllegalStateException("Cannot find current Airbyte version from .env file");
  }

  /**
   * Turn a migration version to airbyte version and drop the migration id. E.g. "0.29.10.004" ->
   * "0.29.10".
   */
  @VisibleForTesting
  static AirbyteVersion getAirbyteVersion(MigrationVersion version) {
    String[] splits = version.getVersion().split("\\.");
    return new AirbyteVersion(splits[0], splits[1], splits[2]);
  }

  /**
   * Extract the major, minor, and patch version and join them with underscore. E.g. "0.29.10-alpha"
   * -> "0_29_10",
   */
  @VisibleForTesting
  static String formatAirbyteVersion(AirbyteVersion version) {
    return String.format("%s_%s_%s", version.getMajorVersion(), version.getMinorVersion(), version.getPatchVersion());
  }

  /**
   * Extract the migration id. E.g. "0.29.10.001" -> "001".
   */
  @VisibleForTesting
  static String getMigrationId(MigrationVersion version) {
    return version.getVersion().split("\\.")[3];
  }

  private static MigrationVersion getNextMigrationVersion(FlywayDatabaseMigrator migrator) {
    Optional<MigrationVersion> lastMigrationVersion = getLastMigrationVersion(migrator);
    AirbyteVersion currentAirbyteVersion = getCurrentAirbyteVersion();
    return getNextMigrationVersion(currentAirbyteVersion, lastMigrationVersion);
  }

  @VisibleForTesting
  @SuppressWarnings("OptionalUsedAsFieldOrParameterType")
  static MigrationVersion getNextMigrationVersion(AirbyteVersion currentAirbyteVersion, Optional<MigrationVersion> lastMigrationVersion) {
    // When there is no migration, use the current airbyte version.
    if (lastMigrationVersion.isEmpty()) {
      LOGGER.info("No migration exists. Use the current airbyte version {}", currentAirbyteVersion);
      return MigrationVersion.fromVersion(String.format("%s_001", formatAirbyteVersion(currentAirbyteVersion)));
    }

    // When the current airbyte version is greater, use the airbyte version.
    MigrationVersion migrationVersion = lastMigrationVersion.get();
    AirbyteVersion migrationAirbyteVersion = getAirbyteVersion(migrationVersion);
    if (currentAirbyteVersion.patchVersionCompareTo(migrationAirbyteVersion) > 0) {
      LOGGER.info(
          "Use the current airbyte version ({}), since it is greater than the last migration version ({})",
          currentAirbyteVersion,
          migrationAirbyteVersion);
      return MigrationVersion.fromVersion(String.format("%s_001", formatAirbyteVersion(currentAirbyteVersion)));
    }

    // When the last migration version is greater, which usually does not happen, use the migration
    // version.
    LOGGER.info(
        "Use the last migration version ({}), since it is greater than or equal to the current airbyte version ({})",
        migrationAirbyteVersion,
        currentAirbyteVersion);
    String lastMigrationId = getMigrationId(migrationVersion);
    System.out.println("lastMigrationId: " + lastMigrationId);
    String nextMigrationId = String.format("%03d", Integer.parseInt(lastMigrationId) + 1);
    System.out.println("nextMigrationId: " + nextMigrationId);
    return MigrationVersion.fromVersion(String.format("%s_%s", migrationAirbyteVersion.getVersion(), nextMigrationId));
  }

}
