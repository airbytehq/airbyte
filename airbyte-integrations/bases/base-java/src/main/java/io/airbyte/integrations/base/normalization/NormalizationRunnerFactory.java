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

package io.airbyte.integrations.base.normalization;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.normalization.NormalizationRunner.NoOpNormalizationRunner;
import java.util.Map;
import java.util.Optional;

public class NormalizationRunnerFactory {

  public static final String BASIC_NORMALIZATION_KEY = "basic_normalization";

  private static final Map<String, DefaultNormalizationRunner.DestinationType> NORMALIZATION_MAPPING =
      ImmutableMap.<String, DefaultNormalizationRunner.DestinationType>builder()
          .put("io.airbyte.integrations.destination.bigquery.BigQueryDestination", DefaultNormalizationRunner.DestinationType.BIGQUERY)
          .put("io.airbyte.integrations.destination.postgres.PostgresDestination", DefaultNormalizationRunner.DestinationType.POSTGRES)
          .put("io.airbyte.integrations.destination.snowflake.SnowflakeDestination", DefaultNormalizationRunner.DestinationType.SNOWFLAKE)
          .build();

  public static NormalizationRunner create(String className, JsonNode config) {
    if (!shouldNormalize(config)) {
      return new NoOpNormalizationRunner();
    }

    if (NORMALIZATION_MAPPING.containsKey(className)) {
      return new DefaultNormalizationRunner(NORMALIZATION_MAPPING.get(className));
    } else {
      throw new IllegalStateException(
          String.format("Requested normalization for %s, but it is not included in the normalization mapping.", className));
    }
  }

  private static boolean shouldNormalize(JsonNode config) {
    return Optional.ofNullable(config.get(BASIC_NORMALIZATION_KEY))
        .map(JsonNode::asBoolean)
        .orElse(false);
  }

}
