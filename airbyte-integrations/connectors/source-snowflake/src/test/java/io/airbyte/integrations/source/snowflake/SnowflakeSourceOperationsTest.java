/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

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
    Assertions.assertEquals(SnowflakeSourceOperations.SQL_DIALECT, airbyteSourceType.get("dialect").asText());
    Assertions.assertEquals(jdbcType.getName(), airbyteSourceType.get("type").asText());
  }

  @Test
  public void testAirbyteTypeMappings() {

    // VARCHAR and TEXT
    Assertions.assertEquals(JsonSchemaType.STRING, sourceOps.getAirbyteType(SnowflakeType.TEXT));
    // TODO: Add test for Snowflake 'TEXT' data type
    Assertions.assertEquals(SnowflakeType.VARIANT, sourceOps.getDatabaseFieldType("VARIANT"));
    Assertions.assertEquals(JsonSchemaType.STRING, sourceOps.getAirbyteType(sourceOps.getDatabaseFieldType("VARIANT")));

    // INT, BIGINT, FIXED, etc.
    // JsonSchemaType airbyteInt = new JsonSchemaType(Map.of("$ref",
    // "WellKnownTypes.json#/definitions/Integer"));
    // Assertions.assertEquals(JsonSchemaType.INTEGER, sourceOps.getAirbyteType(SnowflakeType.INTEGER));
    Assertions.assertEquals(JsonSchemaType.NUMBER, sourceOps.getAirbyteType(SnowflakeType.FIXED));
    // Assertions.assertEquals(JsonSchemaType.INTEGER, sourceOps.getAirbyteType(SnowflakeType.));
    // Assertions.assertEquals(JsonSchemaType.INTEGER, sourceOps.getAirbyteType(SnowflakeType.));

    // TIME, TIMESTAMP, etc.
    Map<String, Object> jsonSchemaForTime = Map.of(
        "type", "string",
        "format", "time",
        "airbyte_type", "time_without_timezone");
    Assertions.assertEquals(jsonSchemaForTime, sourceOps.getAirbyteType(SnowflakeType.TIME).getJsonSchemaTypeMap());
    Map<String, Object> jsonSchemaForDatetime = Map.of(
        "type", "string",
        "format", "date-time",
        "airbyte_type", "timestamp_without_timezone");
    Assertions.assertEquals(jsonSchemaForDatetime, sourceOps.getAirbyteType(SnowflakeType.TIMESTAMP_NTZ).getJsonSchemaTypeMap());

    // TODO: Add test for Snowflake 'VARIANT' data type
    // Assertions.assertEquals(JsonSchemaType.STRING,
    // sourceOps.getAirbyteType(JDBCType.valueOf("VARIANT")));
  }

}
