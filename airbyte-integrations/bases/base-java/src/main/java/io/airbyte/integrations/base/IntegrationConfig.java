/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import com.google.common.base.Preconditions;
import java.nio.file.Path;
import java.util.Objects;
import java.util.Optional;

public class IntegrationConfig {

  private final Command command;
  private final Path configPath;
  private final Path catalogPath;
  private final Path statePath;

  private IntegrationConfig(final Command command, final Path configPath, final Path catalogPath, final Path statePath) {
    this.command = command;
    this.configPath = configPath;
    this.catalogPath = catalogPath;
    this.statePath = statePath;
  }

  public static IntegrationConfig spec() {
    return new IntegrationConfig(Command.SPEC, null, null, null);
  }

  public static IntegrationConfig check(final Path config) {
    Preconditions.checkNotNull(config);
    return new IntegrationConfig(Command.CHECK, config, null, null);
  }

  public static IntegrationConfig discover(final Path config) {
    Preconditions.checkNotNull(config);
    return new IntegrationConfig(Command.DISCOVER, config, null, null);
  }

  public static IntegrationConfig read(final Path configPath, final Path catalogPath, final Path statePath) {
    Preconditions.checkNotNull(configPath);
    Preconditions.checkNotNull(catalogPath);
    return new IntegrationConfig(Command.READ, configPath, catalogPath, statePath);
  }

  public static IntegrationConfig write(final Path configPath, final Path catalogPath) {
    Preconditions.checkNotNull(configPath);
    Preconditions.checkNotNull(catalogPath);
    return new IntegrationConfig(Command.WRITE, configPath, catalogPath, null);
  }

  public Command getCommand() {
    return command;
  }

  public Path getConfigPath() {
    Preconditions.checkState(command != Command.SPEC);
    return configPath;
  }

  public Path getCatalogPath() {
    Preconditions.checkState(command == Command.READ || command == Command.WRITE);
    return catalogPath;
  }

  public Optional<Path> getStatePath() {
    Preconditions.checkState(command == Command.READ);
    return Optional.ofNullable(statePath);
  }

  @Override
  public String toString() {
    return "IntegrationConfig{" +
        "command=" + command +
        ", configPath='" + configPath + '\'' +
        ", catalogPath='" + catalogPath + '\'' +
        ", statePath='" + statePath + '\'' +
        '}';
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final IntegrationConfig that = (IntegrationConfig) o;
    return command == that.command &&
        Objects.equals(configPath, that.configPath) &&
        Objects.equals(catalogPath, that.catalogPath) &&
        Objects.equals(statePath, that.statePath);
  }

  @Override
  public int hashCode() {
    return Objects.hash(command, configPath, catalogPath, statePath);
  }

}
