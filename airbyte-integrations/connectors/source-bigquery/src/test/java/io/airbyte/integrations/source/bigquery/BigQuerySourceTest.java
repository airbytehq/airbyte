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

package io.airbyte.integrations.source.bigquery;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import java.io.IOException;
import org.junit.jupiter.api.Test;

class BigQuerySourceTest {

  @Test
  public void testEmptyDatasetIdInConfig() throws IOException {
    JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config_empty_datasetid.json"));
    JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertTrue(dbConfig.get(BigQuerySource.CONFIG_DATASET_ID).isEmpty());
  }

  @Test
  public void testConfig() throws IOException {
    JsonNode configJson = Jsons.deserialize(MoreResources.readResource("test_config.json"));
    JsonNode dbConfig = new BigQuerySource().toDatabaseConfig(configJson);
    assertEquals("dataset", dbConfig.get(BigQuerySource.CONFIG_DATASET_ID).asText());
    assertEquals("project", dbConfig.get(BigQuerySource.CONFIG_PROJECT_ID).asText());
    assertEquals("credentials", dbConfig.get(BigQuerySource.CONFIG_CREDS).asText());
  }

}
