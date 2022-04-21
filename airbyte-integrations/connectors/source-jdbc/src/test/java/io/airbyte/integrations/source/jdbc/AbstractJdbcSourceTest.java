package io.airbyte.integrations.source.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.PostgresJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.Source;
import org.junit.jupiter.api.Test;

import java.sql.JDBCType;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

public class AbstractJdbcSourceTest {

    private JsonNode buildConfigNoJdbcParameters() {
        return Jsons.jsonNode(ImmutableMap.of(
                "host", "localhost",
                "port", 1337,
                "username", "user",
                "database", "db"));
    }

    private JsonNode buildConfigWithExtraJdbcParameters(final String extraParam) {
        return Jsons.jsonNode(ImmutableMap.of(
                "host", "localhost",
                "port", 1337,
                "username", "user",
                "database", "db",
                "jdbc_url_params", extraParam));
    }

    @Test
    void testNoExtraParamsNoDefault() {
        final Map<String, String> connectionProperties = new TestJdbcSource().getConnectionProperties(buildConfigNoJdbcParameters());

        final Map<String, String> expectedProperties = ImmutableMap.of();
        assertEquals(expectedProperties, connectionProperties);
    }

    @Test
    void testNoExtraParamsWithDefault() {
        final Map<String, String> defaultProperties = ImmutableMap.of("A_PARAMETER", "A_VALUE");

        final Map<String, String> connectionProperties = new TestJdbcSource(defaultProperties).getConnectionProperties(
                buildConfigNoJdbcParameters());

        assertEquals(defaultProperties, connectionProperties);
    }

    @Test
    void testExtraParamNoDefault() {
        final String extraParam = "key1=value1&key2=value2&key3=value3";
        final Map<String, String> connectionProperties = new TestJdbcSource().getConnectionProperties(
                buildConfigWithExtraJdbcParameters(extraParam));
        final Map<String, String> expectedProperties = ImmutableMap.of(
                "key1", "value1",
                "key2", "value2",
                "key3", "value3");
        assertEquals(expectedProperties, connectionProperties);
    }

    @Test
    void testExtraParamWithDefault() {
        final Map<String, String> defaultProperties = ImmutableMap.of("A_PARAMETER", "A_VALUE");
        final String extraParam = "key1=value1&key2=value2&key3=value3";
        final Map<String, String> connectionProperties = new TestJdbcSource(defaultProperties).getConnectionProperties(
                buildConfigWithExtraJdbcParameters(extraParam));
        final Map<String, String> expectedProperties = ImmutableMap.of(
                "A_PARAMETER", "A_VALUE",
                "key1", "value1",
                "key2", "value2",
                "key3", "value3");
        assertEquals(expectedProperties, connectionProperties);
    }

    @Test
    void testExtraParameterEqualToDefault() {
        final Map<String, String> defaultProperties = ImmutableMap.of("key1", "value1");
        final String extraParam = "key1=value1&key2=value2&key3=value3";
        final Map<String, String> connectionProperties = new TestJdbcSource(defaultProperties).getConnectionProperties(
                buildConfigWithExtraJdbcParameters(extraParam));
        final Map<String, String> expectedProperties = ImmutableMap.of(
                "key1", "value1",
                "key2", "value2",
                "key3", "value3");
        assertEquals(expectedProperties, connectionProperties);
    }

    @Test
    void testExtraParameterDiffersFromDefault() {
        final Map<String, String> defaultProperties = ImmutableMap.of("key1", "value0");
        final String extraParam = "key1=value1&key2=value2&key3=value3";

        assertThrows(IllegalArgumentException.class, () -> new TestJdbcSource(defaultProperties).getConnectionProperties(
                buildConfigWithExtraJdbcParameters(extraParam)));
    }

    @Test
    void testInvalidExtraParam() {
        final String extraParam = "key1=value1&sdf&";
        assertThrows(IllegalArgumentException.class,
                () -> new TestJdbcSource().getConnectionProperties(buildConfigWithExtraJdbcParameters(extraParam)));
    }

    static class TestJdbcSource extends AbstractJdbcSource<JDBCType> implements Source {

        private final Map<String, String> defaultProperties;

        public TestJdbcSource() {
            this(new HashMap<>());
        }

        public TestJdbcSource(final Map<String, String> defaultProperties) {
            super("", new PostgresJdbcStreamingQueryConfiguration(), JdbcUtils.getDefaultSourceOperations());
            this.defaultProperties = defaultProperties;
        }

        @Override
        protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
            return defaultProperties;
        }

        @Override
        public JsonNode toDatabaseConfig(final JsonNode config) {
            return config;
        }

        @Override
        public Set<String> getExcludedInternalNameSpaces() {
            return null;
        }

    }
}
