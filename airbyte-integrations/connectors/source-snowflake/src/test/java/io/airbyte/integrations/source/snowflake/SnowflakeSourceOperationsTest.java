/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import static io.airbyte.integrations.source.snowflake.SnowflakeSourceOperations.SQL_DIALECT;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.JDBCType;
import java.util.Map;
import net.snowflake.client.jdbc.SnowflakeType;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

public class SnowflakeSourceOperationsTest {

  SnowflakeSourceOperations sourceOps = new SnowflakeSourceOperations();

  @ParameterizedTest
  @EnumSource(JDBCType.class)
  public void testGetAirbyteSourceType(JDBCType jdbcType) {
    SnowflakeSourceOperations sourceOps = new SnowflakeSourceOperations();
    JsonNode airbyteSourceType = sourceOps.getAirbyteSourceType(jdbcType);
    Assertions.assertNotNull(airbyteSourceType);
    Assertions.assertEquals(SQL_DIALECT, airbyteSourceType.get("dialect").asText());
    Assertions.assertEquals(jdbcType.getName(), airbyteSourceType.get("type").asText());
  }

  @Test
  public void testAirbyteTypeMappings() {

    // VARCHAR and TEXT
    Assertions.assertEquals(JsonSchemaType.STRING, sourceOps.getAirbyteType(JDBCType.VARCHAR));
    // TODO: Add test for Snowflake 'TEXT' data type
    Assertions.assertEquals(SnowflakeType.VARIANT, sourceOps.getDatabaseFieldType("VARIANT"));
    Assertions.assertEquals(JsonSchemaType.STRING, sourceOps.getAirbyteType(sourceOps.getDatabaseFieldType("VARIANT")));

    // INT, BIGINT, etc.
    Assertions.assertEquals(JsonSchemaType.INTEGER, sourceOps.getAirbyteType(JDBCType.BIGINT));
    Assertions.assertEquals(JsonSchemaType.INTEGER, sourceOps.getAirbyteType(JDBCType.INTEGER));
    Assertions.assertEquals(JsonSchemaType.INTEGER, sourceOps.getAirbyteType(JDBCType.SMALLINT));
    Assertions.assertEquals(JsonSchemaType.INTEGER, sourceOps.getAirbyteType(JDBCType.TINYINT));

    // TIME, TIMESTAMP, etc.
    Map<String, Object> jsonSchemaForTime = Map.of(
        "type", "string",
        "format", "time",
        "airbyte_type", "time_without_timezone");
    Assertions.assertEquals(jsonSchemaForTime, sourceOps.getAirbyteType(JDBCType.TIME).getJsonSchemaTypeMap());
    Map<String, Object> jsonSchemaForDatetime = Map.of(
        "type", "string",
        "format", "date-time",
        "airbyte_type", "timestamp_without_timezone");
    Assertions.assertEquals(jsonSchemaForDatetime, sourceOps.getAirbyteType(JDBCType.TIMESTAMP).getJsonSchemaTypeMap());

    // TODO: Add test for Snowflake 'VARIANT' data type
    // Assertions.assertEquals(JsonSchemaType.STRING,
    // sourceOps.getAirbyteType(JDBCType.valueOf("VARIANT")));
  }

}
