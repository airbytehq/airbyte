package io.airbyte.integrations.source.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.JsonSchemaType;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

import java.sql.JDBCType;
import java.util.Map;

import static io.airbyte.integrations.source.snowflake.SnowflakeSourceOperations.SQL_DIALECT;

public class SnowflakeSourceOperationsTest {

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
        SnowflakeSourceOperations sourceOps = new SnowflakeSourceOperations();

        // VARCHAR and TEXT
        JDBCType jdbcTypeForVarchar = JDBCType.VARCHAR;
        JsonSchemaType jsonSchemaTypeForString = JsonSchemaType.STRING;
        Map<String, Object> jsonSchemaForString = Map.of(
            "type", "string",
            "airbyte_type", "string"
        );
        Assertions.assertEquals(jsonSchemaTypeForString, sourceOps.getAirbyteType(jdbcTypeForVarchar));

        // INT, BIGINT, etc.
        JDBCType jdbcTypeForBigint = JDBCType.BIGINT;
        JsonSchemaType jsonSchemaTypeForInteger = JsonSchemaType.INTEGER;
        Map<String, Object> jsonSchemaForInt = Map.of(
            "type", "number",
            "airbyte_type", "integer"
        );
        Assertions.assertEquals(jsonSchemaTypeForInteger, sourceOps.getAirbyteType(jdbcTypeForBigint));
 
        // TIME
        JDBCType jdbcTypeForTime = JDBCType.TIME;
        JsonSchemaType jsonSchemaTypeForTime = JsonSchemaType.TIME_WITHOUT_TIMEZONE_V1;
        Assertions.assertEquals(jdbcTypeForTime, sourceOps.getAirbyteType(jsonSchemaTypeForTime));
    }
    
}