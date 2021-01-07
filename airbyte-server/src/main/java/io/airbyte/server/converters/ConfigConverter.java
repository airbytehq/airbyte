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

package io.airbyte.server.converters;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.ConfigSchema;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class ConfigConverter {

  private static final String CONFIG_FOLDER_NAME = "AirbyteConfig";

  private final Path storageRoot;
  private final String version;

  public ConfigConverter(final Path storageRoot, final String version) {
    this.storageRoot = storageRoot;
    this.version = version;
  }

  private Path buildConfigPath(ConfigSchema schemaType) {
    return storageRoot.resolve(CONFIG_FOLDER_NAME)
        .resolve(String.format("%s.yaml", schemaType.toString()));
  }

  public <T> void writeConfig(ConfigSchema schemaType, T config) throws IOException {
    final Path configPath = buildConfigPath(schemaType);
    Files.createDirectories(configPath.getParent());
    Files.writeString(configPath, Yamls.serialize(new ConfigWrapper<>(version, config)));
  }

  public <T> T readConfig(ConfigSchema schemaType) throws IOException {
    final Path configPath = buildConfigPath(schemaType);
    final String configStr = Files.readString(configPath);
    ConfigWrapper wrapper = Yamls.deserialize(configStr, ConfigWrapper.class);
    if (!version.equals(wrapper.getAirbyteVersion())) {
      throw new IOException(String.format("Mismatch version, expected %s", version));
    }
    return (T) wrapper.getAirbyteConfig();
  }

  static private class ConfigWrapper<T> {

    @JsonProperty("airbyteVersion")
    private final String airbyteVersion;

    @JsonProperty("airbyteConfig")
    private final T airbyteConfig;

    public ConfigWrapper(final String version, T config) {
      airbyteVersion = version;
      airbyteConfig = config;
    }

    public String getAirbyteVersion() {
      return airbyteVersion;
    }

    public T getAirbyteConfig() {
      return airbyteConfig;
    }

  }

}
