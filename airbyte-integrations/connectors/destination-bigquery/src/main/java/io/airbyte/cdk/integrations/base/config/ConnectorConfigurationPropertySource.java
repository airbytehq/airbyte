package io.airbyte.cdk.integrations.base.config;

import com.fasterxml.jackson.core.type.TypeReference;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.micronaut.context.env.MapPropertySource;
import io.micronaut.core.cli.CommandLine;
import io.micronaut.core.util.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Path;
import java.util.AbstractMap;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.ARGS_CATALOG_KEY;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.ARGS_CONFIG_KEY;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.ARGS_STATE_KEY;

public class ConnectorConfigurationPropertySource extends MapPropertySource {

    private static final Logger LOGGER = LoggerFactory.getLogger(ConnectorConfigurationPropertySource.class);

    private static final String PREFIX_FORMAT = "%s.%s";
    private static final String ROOT_CONFIGURATION_PROPERTY_KEY = "airbyte.connector";
    private static final String CONNECTOR_OPERATION = ROOT_CONFIGURATION_PROPERTY_KEY + ".operation";
    public static final String CONNECTOR_CONFIG_PREFIX = ROOT_CONFIGURATION_PROPERTY_KEY + ".config";
    public static final String CONNECTOR_CATALOG_PREFIX = ROOT_CONFIGURATION_PROPERTY_KEY + ".catalog";
    public static final String CONNECTOR_STATE_PREFIX = ROOT_CONFIGURATION_PROPERTY_KEY + ".state";

    public ConnectorConfigurationPropertySource(final CommandLine commandLine) {
        super("connector", resolveValues(commandLine));
    }

    private static Map<String, Object> resolveValues(final CommandLine commandLine) {
        final Map<String,Object> values = new HashMap<>();
        values.put(CONNECTOR_OPERATION, commandLine.getRawArguments()[0]);
        values.putAll(loadFile((String)commandLine.optionValue(ARGS_CONFIG_KEY), CONNECTOR_CONFIG_PREFIX));
        values.putAll(loadFileContents((String)commandLine.optionValue(ARGS_CATALOG_KEY), String.format(PREFIX_FORMAT, CONNECTOR_CATALOG_PREFIX, "configured")));
        values.putAll(loadFileContents((String)commandLine.optionValue(ARGS_STATE_KEY), String.format(PREFIX_FORMAT, CONNECTOR_STATE_PREFIX, "state")));
        LOGGER.debug("Resolved values: {}", values);
        return values;
    }

    private static Map<String,Object> loadFile(final String propertyFile, final String prefix) {
        if (StringUtils.hasText(propertyFile)) {
            final Path propertyFilePath = Path.of(propertyFile);
            if (propertyFilePath.toFile().exists()) {
                final Map<String, Object> properties = Jsons.deserialize(IOs.readFile(propertyFilePath), new MapTypeReference());
                return flatten(properties, prefix).collect(Collectors.toMap(e -> e.getKey(), e -> e.getValue()));
            } else {
                LOGGER.warn("Property file '{}', not found for prefix '{}'.", propertyFile, prefix);
                return Map.of();
            }
        } else {
            return Map.of();
        }
    }

    private static Map<String,Object> loadFileContents(final String propertyFile, final String prefix) {
        if (StringUtils.hasText(propertyFile)) {
            final Path propertyFilePath = Path.of(propertyFile);
            if (propertyFilePath.toFile().exists()) {
                return Map.of(prefix, IOs.readFile(propertyFilePath));
            } else {
                LOGGER.warn("Property file '{}', not found for prefix '{}'.", propertyFile, prefix);
                return Map.of();
            }
        } else {
            return Map.of();
        }
    }

    private static Stream<Map.Entry<String, Object>> flatten(final Map<String,Object> map, final String prefix) {
        return map.entrySet().stream().flatMap(e -> flattenValue(e, prefix));
    }

    @SuppressWarnings("unchecked")
    private static Stream<Map.Entry<String, Object>> flattenValue(final Map.Entry<String, Object> entry, final String prefix) {
        if(entry.getValue() instanceof Map) {
            return flatten((Map<String, Object>)entry.getValue(), String.format(PREFIX_FORMAT, prefix, entry.getKey()));
        } else {
            return Stream.of(new AbstractMap.SimpleEntry<>(String.format(PREFIX_FORMAT, prefix, entry.getKey()), entry.getValue()));
        }
    }

    private static class MapTypeReference extends TypeReference<Map<String,Object>> { }
}
