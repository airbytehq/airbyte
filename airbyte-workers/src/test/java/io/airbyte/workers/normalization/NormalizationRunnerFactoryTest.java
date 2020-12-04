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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.workers.normalization.DefaultNormalizationRunner.DestinationType;
import io.airbyte.workers.normalization.NormalizationRunner.NoOpNormalizationRunner;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.util.Collections;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

class NormalizationRunnerFactoryTest {

  private static final JsonNode CONFIG_WITH_NORMALIZATION = Jsons.jsonNode(ImmutableMap.of("basic_normalization", true));
  private ProcessBuilderFactory pbf;
  private NormalizationRunnerFactory normalizationRunnerFactory;

  @BeforeEach
  void setup() {
    pbf = mock(ProcessBuilderFactory.class);
    normalizationRunnerFactory = new NormalizationRunnerFactory("organic");
  }

  @Test
  void testMappings() {
    assertEquals(DestinationType.BIGQUERY,
        ((DefaultNormalizationRunner) normalizationRunnerFactory.create(
            "airbyte/destination-bigquery:0.1.0", pbf, CONFIG_WITH_NORMALIZATION)).getDestinationType());
    assertEquals(DestinationType.POSTGRES,
        ((DefaultNormalizationRunner) normalizationRunnerFactory.create(
            "airbyte/destination-postgres:0.1.0", pbf, CONFIG_WITH_NORMALIZATION)).getDestinationType());
    assertEquals(DestinationType.SNOWFLAKE,
        ((DefaultNormalizationRunner) normalizationRunnerFactory.create(
            "airbyte/destination-snowflake:0.1.0", pbf, CONFIG_WITH_NORMALIZATION)).getDestinationType());
    assertThrows(IllegalStateException.class,
        () -> normalizationRunnerFactory.create("airbyte/destination-csv:0.1.0", pbf, CONFIG_WITH_NORMALIZATION));
  }

  @Test
  void testShouldNotNormalize() {
    assertTrue(normalizationRunnerFactory.create("airbyte/destination-bigquery:0.1.0", pbf,
        Jsons.jsonNode(Collections.emptyMap())) instanceof NoOpNormalizationRunner);
  }

}
