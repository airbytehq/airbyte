package io.airbyte.integrations.destination.snowflake;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import java.io.IOException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SnowflakeCopyGcsDestinationTest {

  final SnowflakeCopyGcsDestination copyGcsDestination = new SnowflakeCopyGcsDestination();
  JsonNode config;

  @BeforeEach
  public void setup() throws IOException {
    config = spy(Jsons.deserialize(MoreResources.readResource("insert_config.json"), JsonNode.class));
  }

  @Test
  void getNameTransformer() {
    ExtendedNameTransformer actualNameTransformer = copyGcsDestination.getNameTransformer();
    assertEquals(actualNameTransformer.getClass(), SnowflakeSQLNameTransformer.class);
  }

  @Test
  void getDatabase() throws Exception {
    copyGcsDestination.getDatabase(config);
    verify(config, times(1)).get("host");
    verify(config, times(1)).get("username");
    verify(config, times(1)).get("password");
    verify(config, times(1)).get("warehouse");
    verify(config, times(1)).get("database");
    verify(config, times(1)).get("role");
    verify(config, times(1)).get("schema");
  }

  @Test
  void getSqlOperations() {
    SqlOperations sqlOperations = copyGcsDestination.getSqlOperations();
    assertEquals(SnowflakeSqlOperations.class, sqlOperations.getClass());
  }
}