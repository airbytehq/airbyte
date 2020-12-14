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

package io.airbyte.workers.normalization;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.normalization.NormalizationRunner.NoOpNormalizationRunner;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.util.Map;
import java.util.Optional;

public class NormalizationRunnerFactory {

  private static final Map<String, DefaultNormalizationRunner.DestinationType> NORMALIZATION_MAPPING =
      ImmutableMap.<String, DefaultNormalizationRunner.DestinationType>builder()
          .put("airbyte/destination-bigquery", DefaultNormalizationRunner.DestinationType.BIGQUERY)
          .put("airbyte/destination-postgres", DefaultNormalizationRunner.DestinationType.POSTGRES)
          .put("airbyte/destination-redshift", DefaultNormalizationRunner.DestinationType.REDSHIFT)
          .put("airbyte/destination-snowflake", DefaultNormalizationRunner.DestinationType.SNOWFLAKE)
          .build();

  public static NormalizationRunner create(String imageName, ProcessBuilderFactory pbf, JsonNode config) {
    if (!shouldNormalize(config)) {
      return new NoOpNormalizationRunner();
    }

    final String imageNameWithoutTag = imageName.split(":")[0];

    if (NORMALIZATION_MAPPING.containsKey(imageNameWithoutTag)) {
      return new DefaultNormalizationRunner(NORMALIZATION_MAPPING.get(imageNameWithoutTag), pbf);
    } else {
      throw new IllegalStateException(
          String.format("Requested normalization for %s, but it is not included in the normalization mapping.", imageName));
    }
  }

  private static boolean shouldNormalize(JsonNode config) {
    return Optional.ofNullable(config.get(WorkerConstants.BASIC_NORMALIZATION_KEY))
        .map(JsonNode::asBoolean)
        .orElse(false);
  }

}
