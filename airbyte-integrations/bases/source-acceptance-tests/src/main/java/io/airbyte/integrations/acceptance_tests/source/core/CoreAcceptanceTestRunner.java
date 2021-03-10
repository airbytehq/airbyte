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

package io.airbyte.integrations.acceptance_tests.source.core;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public class CoreAcceptanceTestRunner extends CoreAcceptanceTest {

  public static class Config {

    public Config(String connectorImage,
                  JsonNode expectedSpec,
                  JsonNode validConfig,
                  JsonNode invalidConfig,
                  ConfiguredAirbyteCatalog configuredCatalog) {
      this.connectorImage = connectorImage;
      this.expectedSpec = expectedSpec;
      this.validConfig = validConfig;
      this.invalidConfig = invalidConfig;
      this.configuredCatalog = configuredCatalog;
    }

    String connectorImage;
    JsonNode expectedSpec;
    JsonNode validConfig;
    JsonNode invalidConfig;
    ConfiguredAirbyteCatalog configuredCatalog;

  }

  public static Config CONFIG;

  protected JsonNode getValidConfig() {
    return CONFIG.validConfig;
  }

  @Override
  protected JsonNode getInvalidConfig() {
    return CONFIG.invalidConfig;
  }

  protected JsonNode getExpectedSpec() {
    return CONFIG.expectedSpec;
  }

  protected String getConnectorImage() {
    return CONFIG.connectorImage;
  }

  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CONFIG.configuredCatalog;
  }

}
