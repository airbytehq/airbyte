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

package io.airbyte.integrations.acceptance_tests.source.incremental;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public class IncrementalAcceptanceTestRunner extends IncrementalAcceptanceTest {

  public static class Config {

    String connectorImage;
    JsonNode connectorConfig;
    ConfiguredAirbyteCatalog configuredCatalog;

    public Config(String connectorImage, JsonNode connectorConfig, ConfiguredAirbyteCatalog configuredCatalog) {
      this.connectorImage = connectorImage;
      this.connectorConfig = connectorConfig;
      this.configuredCatalog = configuredCatalog;
    }

  }

  public static Config CONFIG;

  @Override
  protected String getConnectorImage() {
    return CONFIG.connectorImage;
  }

  @Override
  protected JsonNode getConnectorConfig() {
    return CONFIG.connectorConfig;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CONFIG.configuredCatalog;
  }

}
