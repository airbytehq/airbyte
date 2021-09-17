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

import static io.airbyte.integrations.source.bigquery.BigQuerySource.CONFIG_CREDS;
import static io.airbyte.integrations.source.bigquery.BigQuerySource.CONFIG_DATASET_ID;
import static io.airbyte.integrations.source.bigquery.BigQuerySource.CONFIG_PROJECT_ID;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.bigquery.BigQueryDatabase;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.List;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class BigQuerySourceTest {

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
  private static final String STREAM_NAME = "id_and_name";

  private BigQueryDatabase database;
  private Dataset dataset;
  private JsonNode config;

  @BeforeEach
  void setUp() throws IOException, SQLException {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    final String credentialsJsonString = new String(Files.readAllBytes(CREDENTIALS_PATH));

    final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString);
    final String projectId = credentialsJson.get(CONFIG_PROJECT_ID).asText();
    final String datasetLocation = "US";

    final String datasetId = Strings.addRandomSuffix("airbyte_tests", "_", 8);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(CONFIG_PROJECT_ID, projectId)
        .put(CONFIG_CREDS, credentialsJsonString)
        .put(CONFIG_DATASET_ID, datasetId)
        .build());

    database = new BigQueryDatabase(config.get(CONFIG_PROJECT_ID).asText(), credentialsJsonString);

    final DatasetInfo datasetInfo =
        DatasetInfo.newBuilder(config.get(CONFIG_DATASET_ID).asText()).setLocation(datasetLocation).build();
    dataset = database.getBigQuery().create(datasetInfo);

    database.execute(
        "CREATE TABLE " + datasetId
            + ".id_and_name(id INT64, array_val ARRAY<STRUCT<key string, value STRUCT<string_val string>>>, object_val STRUCT<val_array ARRAY<STRUCT<value_str1 string>>, value_str2 string>);");
    database.execute(
        "INSERT INTO " + datasetId
            + ".id_and_name (id, array_val, object_val) VALUES "
            + "(1, [STRUCT('test1_1', STRUCT('struct1_1')), STRUCT('test1_2', STRUCT('struct1_2'))], STRUCT([STRUCT('value1_1'), STRUCT('value1_2')], 'test1_1')), "
            + "(2, [STRUCT('test2_1', STRUCT('struct2_1')), STRUCT('test2_2', STRUCT('struct2_2'))], STRUCT([STRUCT('value2_1'), STRUCT('value2_2')], 'test2_1')), "
            + "(3, [STRUCT('test3_1', STRUCT('struct3_1')), STRUCT('test3_2', STRUCT('struct3_2'))], STRUCT([STRUCT('value3_1'), STRUCT('value3_2')], 'test3_1'));");
  }

  @AfterEach
  void tearDown() {
    database.cleanDataSet(dataset.getDatasetId().getDataset());
  }

  @Test
  public void testReadSuccess() throws Exception {
    final List<AirbyteMessage> actualMessages = MoreIterators.toList(new BigQuerySource().read(config, getConfiguredCatalog(), null));

    assertNotNull(actualMessages);
    assertEquals(3, actualMessages.size());
  }

  private ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CatalogHelpers.createConfiguredAirbyteCatalog(
        STREAM_NAME,
        config.get(CONFIG_DATASET_ID).asText(),
        Field.of("id", JsonSchemaPrimitive.NUMBER),
        Field.of("array_val", JsonSchemaPrimitive.ARRAY),
        Field.of("object_val", JsonSchemaPrimitive.OBJECT));
  }

}
