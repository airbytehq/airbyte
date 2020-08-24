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

package io.dataline.scheduler;

import com.google.common.collect.ImmutableMap;
import java.util.Map;
import java.util.UUID;

public class IntegrationConstants {
  public static Map<UUID, IntegrationMapping> SPEC_ID_TO_IMPL =
      ImmutableMap.of(
          UUID.fromString("2168516a-5c9a-4582-90dc-5e3a01e3f607"),
          new IntegrationMapping("dataline/integration-singer-postgres-source"),
          UUID.fromString("71cb2b91-1b2f-4c42-8f4d-f1ab2bd72080"),
          new IntegrationMapping(
              "dataline/integration-singer-postgres-destination",
              "dataline/integration-singer-postgres-destination",
              "dataline/integration-singer-postgres-destination"));

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
