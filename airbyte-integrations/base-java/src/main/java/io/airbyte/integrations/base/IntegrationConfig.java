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

  private IntegrationConfig(Command command, Path configPath, Path catalogPath, Path statePath) {
    this.command = command;
    this.configPath = configPath;
    this.catalogPath = catalogPath;
    this.statePath = statePath;
  }

  public static IntegrationConfig spec() {
    return new IntegrationConfig(Command.SPEC, null, null, null);
  }

  public static IntegrationConfig check(Path config) {
    Preconditions.checkNotNull(config);
    return new IntegrationConfig(Command.CHECK, config, null, null);
  }

  public static IntegrationConfig discover(Path config) {
    Preconditions.checkNotNull(config);
    return new IntegrationConfig(Command.DISCOVER, config, null, null);
  }

  public static IntegrationConfig read(Path configPath, Path catalogPath, Path statePath) {
    Preconditions.checkNotNull(configPath);
    Preconditions.checkNotNull(catalogPath);
    return new IntegrationConfig(Command.READ, configPath, catalogPath, statePath);
  }

  public static IntegrationConfig write(Path configPath, Path catalogPath) {
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
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    IntegrationConfig that = (IntegrationConfig) o;
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
