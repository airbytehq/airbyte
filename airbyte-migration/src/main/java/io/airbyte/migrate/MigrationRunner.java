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

import io.airbyte.commons.io.Archives;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import net.sourceforge.argparse4j.ArgumentParsers;
import net.sourceforge.argparse4j.inf.ArgumentParser;
import net.sourceforge.argparse4j.inf.ArgumentParserException;
import net.sourceforge.argparse4j.inf.Namespace;

public class MigrationRunner {

  public static void run(String[] args) throws IOException {
    final Path workspaceRoot = Files.createTempDirectory(Path.of("/tmp"), "airbyte_migrate");

    MigrateConfig migrateConfig = parse(args);

    if (migrateConfig.getInputPath().toString().endsWith(".tar.gz")) {
      final Path uncompressedInputPath = Files.createDirectories(workspaceRoot.resolve("uncompressed"));
      Archives.extractArchive(migrateConfig.getInputPath(), uncompressedInputPath);
      migrateConfig = new MigrateConfig(
          uncompressedInputPath,
          migrateConfig.getOutputPath(),
          migrateConfig.getTargetVersion());
    }

    new Migrate(workspaceRoot.resolve("migrate")).run(migrateConfig);
  }

  private static MigrateConfig parse(String[] args) {
    final ArgumentParser parser = ArgumentParsers.newFor(Migrate.class.getName()).build()
        .defaultHelp(true)
        .description("Migrate Airbyte Data");

    parser.addArgument("--input")
        .required(true)
        .help("Path to .tar.gz archive or root dir of data to migrate.");

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
    MigrationRunner.run(args);
  }

}
