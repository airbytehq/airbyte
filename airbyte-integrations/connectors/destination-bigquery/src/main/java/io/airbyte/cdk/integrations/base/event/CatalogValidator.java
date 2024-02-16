package io.airbyte.cdk.integrations.base.event;

import io.airbyte.cdk.integrations.base.config.AirbyteConfiguredCatalog;
import io.airbyte.cdk.integrations.base.operation.OperationType;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.context.event.StartupEvent;
import jakarta.inject.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static io.airbyte.cdk.integrations.base.config.ConnectorConfigurationPropertySource.CONNECTOR_OPERATION;

@Singleton
@Requires(bean = AirbyteConfiguredCatalog.class)
@Requires(property = CONNECTOR_OPERATION)
public class CatalogValidator implements ApplicationEventListener<StartupEvent> {

    private static final Logger LOGGER = LoggerFactory.getLogger(CatalogValidator.class);
    private static final ConfiguredAirbyteCatalog EMPTY_CATALOG = new ConfiguredAirbyteCatalog();

    private final String connectorName;
    private final String operation;
    private final AirbyteConfiguredCatalog airbyteConfiguredCatalog;

    public CatalogValidator(
            @Value("${micronaut.application.name}") final String connectorName,
            @Value("${airbyte.connector.operation}") final String operation,
            final AirbyteConfiguredCatalog airbyteConfiguredCatalog) {
        this.connectorName = connectorName;
        this.operation = operation;
        this.airbyteConfiguredCatalog = airbyteConfiguredCatalog;
    }

    @Override
    public void onApplicationEvent(final StartupEvent event) {
        if(requiresCatalog()) {
            if (!EMPTY_CATALOG.equals(airbyteConfiguredCatalog.getConfiguredCatalog())) {
                LOGGER.info("{} connector configured catalog is valid.", connectorName);
            } else {
                throw new IllegalArgumentException("Configured catalog is not valid.");
            }
        }
    }

    private boolean requiresCatalog() {
        return OperationType.READ.name().equalsIgnoreCase(operation) || OperationType.WRITE.name().equalsIgnoreCase(operation);
    }
}
