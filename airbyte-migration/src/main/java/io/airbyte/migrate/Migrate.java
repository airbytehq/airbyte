package io.airbyte.migrate;

import io.airbyte.commons.io.IOs;
import java.nio.file.Path;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

public class Migrate {

  public void run(MigrateConfig migrateConfig) {
    System.out.println("migrateConfig = " + migrateConfig);
    // detect current version.
    // detect desired version.
    // select migrations to run.
    // for each migration to run:
    // run migration
    // write output of each migration to disk.
  }

  private static String getCurrentVersion(Path path) {
    return IOs.readFile(path.resolve("version.txt"));
  }

  private static MigrateConfig parse(String[] args) {
    final ArgumentParser parser = ArgumentParsers.newFor(Migrate.class.getName()).build()
        .defaultHelp(true)
        .description("Migrate Airbyte Data");

    parser.addArgument("--input")
        .required(true)
        .help("Path to data.");

    parser.addArgument("--target-version")
        .required(true)
        .help("Version to upgrade the data to");

    try {
      final Namespace parsed = parser.parseArgs(args);
      final Path dataPath = Path.of(parsed.getString("input"));
      final String targetVersion = parsed.getString("target_version");
      return new MigrateConfig(dataPath, targetVersion);
    } catch (ArgumentParserException e) {
      parser.handleError(e);
      throw new IllegalArgumentException(e);
    }
  }

  public static void main(String[] args) {
    final MigrateConfig migrateConfig = parse(args);
    new Migrate().run(migrateConfig);
  }

  private static class MigrateConfig {
    private final Path data;
    private final String targetVersion;

    public MigrateConfig(Path data, String targetVersion) {
      this.data = data;
      this.targetVersion = targetVersion;
    }

    public Path getData() {
      return data;
    }

    public String getTargetVersion() {
      return targetVersion;
    }

    @Override
    public String toString() {
      return "MigrateConfig{" +
          "data=" + data +
          ", targetVersion='" + targetVersion + '\'' +
          '}';
    }
  }
}
