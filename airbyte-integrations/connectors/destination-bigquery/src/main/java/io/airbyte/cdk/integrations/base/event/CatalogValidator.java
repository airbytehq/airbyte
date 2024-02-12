package io.airbyte.cdk.integrations.base.event;

import io.airbyte.cdk.integrations.base.config.AirbyteConfiguredCatalog;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.context.event.StartupEvent;
import jakarta.inject.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
@Requires(bean = AirbyteConfiguredCatalog.class)
public class CatalogValidator implements ApplicationEventListener<StartupEvent> {

    private static final Logger LOGGER = LoggerFactory.getLogger(CatalogValidator.class);

    private final String connectorName;
    private final AirbyteConfiguredCatalog airbyteConfiguredCatalog;

    public CatalogValidator(
            @Value("${micronaut.application.name}") final String connectorName,
            final AirbyteConfiguredCatalog airbyteConfiguredCatalog) {
        this.connectorName = connectorName;
        this.airbyteConfiguredCatalog = airbyteConfiguredCatalog;
    }

    @Override
    public void onApplicationEvent(final StartupEvent event) {
        airbyteConfiguredCatalog.getConfiguredCatalog();
        LOGGER.info("{} connector configured catalog is valid.", connectorName);
    }
}
