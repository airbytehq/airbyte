/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.bigquery;

import static io.airbyte.integrations.source.bigquery.BigQuerySource.CONFIG_DATASET_ID;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.sql.SQLException;
import java.util.List;
import org.junit.jupiter.api.Test;

public class BigQuerySourceEscapeColumnNameTest extends AbstractBigQuerySourceTest {

  @Override
  public void createTable(String datasetId) throws SQLException {
    // create column name interval which should be escaped
    database.execute("CREATE TABLE " + datasetId + ".id_and_interval(id INT64, `interval` STRING);");
    database.execute("INSERT INTO " + datasetId + ".id_and_interval (id, `interval`) VALUES (1,'picard');");
  }

  @Test
  public void testReadSuccess() throws Exception {
    final List<AirbyteMessage> actualMessages = MoreIterators.toList(new BigQuerySource().read(config, getConfiguredCatalog(), null));
    assertNotNull(actualMessages);
    assertEquals(1, actualMessages.size());

    assertNotNull(actualMessages.get(0).getRecord().getData().get("interval"));
    assertEquals("picard", actualMessages.get(0).getRecord().getData().get("interval").asText());
  }

  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return CatalogHelpers.createConfiguredAirbyteCatalog(
        "id_and_interval",
        config.get(CONFIG_DATASET_ID).asText(),
        Field.of("id", JsonSchemaType.NUMBER),
        Field.of("interval", JsonSchemaType.STRING));
  }

}
