/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate;

import java.nio.file.Path;

public class MigrateConfig {

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

  @Override
  public String toString() {
    return "MigrateConfig{" +
        "inputPath=" + inputPath +
        ", outputPath=" + outputPath +
        ", targetVersion='" + targetVersion + '\'' +
        '}';
  }

}
