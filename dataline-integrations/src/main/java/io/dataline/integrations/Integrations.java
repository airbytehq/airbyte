/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.integrations;

import java.util.UUID;

public enum Integrations {

  POSTGRES_TAP(
      UUID.fromString("2168516a-5c9a-4582-90dc-5e3a01e3f607"),
      new IntegrationMapping("dataline/integration-singer-postgres-source:0.1.1")),
  EXCHANGERATEAPI_IO_TAP(
      UUID.fromString("37eb2ebf-0899-4b22-aba8-8537ec88b5a8"),
      new IntegrationMapping("dataline/integration-singer-exchangerateapi_io-source:0.1.2")),
  STRIPE_TAP(
      UUID.fromString("dd42e77b-24ce-485d-8146-ee6c96d5b454"),
      new IntegrationMapping("dataline/integration-singer-stripe-source:0.1.0")),
  POSTGRES_TARGET(
      UUID.fromString("a6655e6a-838c-4ecb-a28f-ffdcd27ec710"),
      new IntegrationMapping("dataline/integration-singer-postgres-destination:0.1.1")),
  BIGQUERY_TARGET(
      UUID.fromString("e28a1a10-214a-4051-8cf4-79b6f88719cd"),
      new IntegrationMapping("dataline/integration-singer-bigquery-destination:0.1.1"));

  private final UUID specId;
  private final IntegrationMapping integrationMapping;

  // todo (cgardens) - turn this into a map if we have enough integrations that iterating through
  // the enum becomes expensive.
  public static Integrations findBySpecId(UUID specId) {
    for (Integrations value : values()) {
      if (value.getSpecId().equals(specId)) {
        return value;
      }
    }
    throw new RuntimeException("No integrations found with spec id: " + specId);
  }

  Integrations(UUID specId, IntegrationMapping integrationMapping) {
    this.specId = specId;
    this.integrationMapping = integrationMapping;
  }

  public UUID getSpecId() {
    return specId;
  }

  public String getCheckConnectionImage() {
    return integrationMapping.getCheckConnection();
  }

  public String getDiscoverSchemaImage() {
    return integrationMapping.getDiscoverSchema();
  }

  public String getSyncImage() {
    return integrationMapping.getSync();
  }

  public static class IntegrationMapping {

    private final String checkConnection;
    private final String discoverSchema;
    private final String sync;

    public IntegrationMapping(String checkConnection, String discoverSchema, String sync) {
      this.checkConnection = checkConnection;
      this.discoverSchema = discoverSchema;
      this.sync = sync;
    }

    public IntegrationMapping(String image) {
      this(image, image, image);
    }

    public String getCheckConnection() {
      return checkConnection;
    }

    public String getDiscoverSchema() {
      return discoverSchema;
    }

    public String getSync() {
      return sync;
    }

  }

}
