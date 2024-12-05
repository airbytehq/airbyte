/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.bigquery;

import static io.airbyte.integrations.source.bigquery.BigQuerySource.CONFIG_DATASET_ID;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.sql.SQLException;
import java.util.List;
import org.junit.jupiter.api.Test;

public class BigQuerySourceStructRepeatedTest extends AbstractBigQuerySourceTest {

  @Override
  public void createTable(String datasetId) throws SQLException {
    // create column name interval which should be escaped
    database.execute("CREATE TABLE " + datasetId + ".struct_repeated(id int64, key_value_pairs ARRAY<STRUCT<key STRING, value FLOAT64>>);");
    database.execute("INSERT INTO " + datasetId + ".struct_repeated (id, key_value_pairs) VALUES (1, [('a', 0.7), ('b', 0.8), ('c', 1.2)]);");
  }

  @Test
  public void testReadSuccess() throws Exception {
    final List<AirbyteMessage> actualMessages = MoreIterators.toList(new BigQuerySource().read(config, getConfiguredCatalog(), null));

    ObjectMapper mapper = new ObjectMapper();
    // JsonNode actualObj = mapper.readTree("{\"key_value_pairs\":[{ \"key\": \"a\",\"value\": \"0.7\"},
    // {\"key\": \"b\",\"value\": \"0.8\"}, {\"key\": \"c\",\"value\": \"1.2\"}]}");
    JsonNode actualObj = mapper.readTree("[{ \"key\": \"a\",\"value\": 0.7}, {\"key\": \"b\",\"value\": 0.8}, {\"key\": \"c\",\"value\": 1.2}]");

    assertNotNull(actualMessages);
    assertEquals(1, actualMessages.size());

    assertNotNull(actualMessages.get(0).getRecord().getData().get("id"));
    assertEquals(actualObj, actualMessages.get(0).getRecord().getData().get("key_value_pairs"));
  }

  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CatalogHelpers.createConfiguredAirbyteCatalog(
        "struct_repeated",
        config.get(CONFIG_DATASET_ID).asText(),
        Field.of("id", JsonSchemaType.NUMBER),
        Field.of("key_value_pairs", JsonSchemaType.ARRAY));
  }

}
