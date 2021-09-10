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

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;

public interface ConfigPersistence {

  <T> T getConfig(AirbyteConfig configType, String configId, Class<T> clazz) throws ConfigNotFoundException, JsonValidationException, IOException;

  <T> List<T> listConfigs(AirbyteConfig configType, Class<T> clazz) throws JsonValidationException, IOException;

  <T> void writeConfig(AirbyteConfig configType, String configId, T config) throws JsonValidationException, IOException;

  void deleteConfig(AirbyteConfig configType, String configId) throws ConfigNotFoundException, IOException;

  void replaceAllConfigs(Map<AirbyteConfig, Stream<?>> configs, boolean dryRun) throws IOException;

  Map<String, Stream<JsonNode>> dumpConfigs() throws IOException;

  void loadData(ConfigPersistence seedPersistence) throws IOException;

}
