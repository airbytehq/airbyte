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

package io.airbyte.config.persistence.split_secrets;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Map;

/**
 * Data class that provides a way to store the output of a {@link SecretsHelpers} "split" operation
 * which takes a "full config" (including secrets) and creates a "partial config" (secrets removed
 * and has coordinate pointers to a persistence layer).
 *
 * The split methods don't actually update the persistence layer itself. The coordinate to secret
 * payload map in this class allows the system calling "split" to update the persistence with those
 * new coordinate values.
 */
public class SplitSecretConfig {

  private final JsonNode partialConfig;
  private final Map<SecretCoordinate, String> coordinateToPayload;

  public SplitSecretConfig(final JsonNode partialConfig, final Map<SecretCoordinate, String> coordinateToPayload) {
    this.partialConfig = partialConfig;
    this.coordinateToPayload = coordinateToPayload;
  }

  public JsonNode getPartialConfig() {
    return partialConfig;
  }

  public Map<SecretCoordinate, String> getCoordinateToPayload() {
    return coordinateToPayload;
  }

}
