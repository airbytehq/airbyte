package io.airbyte.integrations.destination.jdbc.copy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;

public abstract class SwitchingDestination<T extends Enum<T>> implements Destination {

    private static final Logger LOGGER = LoggerFactory.getLogger(SwitchingDestination.class);

    private final Function<JsonNode, T> configToType;
    private final Map<T, Destination> typeToDestination;

    public SwitchingDestination(Class<T> enumClass, Function<JsonNode, T> configToType, Map<T, Destination> typeToDestination) {
        final Set<T> allEnumConstants = new HashSet<>(Arrays.asList(enumClass.getEnumConstants()));
        final Set<T> supportedEnumConstants = typeToDestination.keySet();

        // check that it isn't possible for configToType to produce something we can't handle
        Preconditions.checkArgument(allEnumConstants.equals(supportedEnumConstants));

        this.configToType = configToType;
        this.typeToDestination = typeToDestination;
    }

    @Override
    public AirbyteConnectionStatus check(JsonNode config) throws Exception {
        final T destinationType = configToType.apply(config);
        LOGGER.info("Using destination type: " + destinationType.name());
        return typeToDestination.get(destinationType).check(config);
    }

    @Override
    public AirbyteMessageConsumer getConsumer(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
        final T destinationType = configToType.apply(config);
        LOGGER.info("Using destination type: " + destinationType.name());
        return typeToDestination.get(destinationType).getConsumer(config, catalog);
    }

}
