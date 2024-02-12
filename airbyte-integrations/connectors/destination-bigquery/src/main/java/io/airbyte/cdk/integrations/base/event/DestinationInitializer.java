package io.airbyte.cdk.integrations.base.event;

import io.airbyte.cdk.integrations.base.DestinationConfig;
import io.airbyte.cdk.integrations.base.config.ConnectorConfiguration;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.context.event.StartupEvent;
import jakarta.inject.Singleton;

@Singleton
@Requires(env = "destination")
public class DestinationInitializer implements ApplicationEventListener<StartupEvent> {

    private final ConnectorConfiguration configuration;
    private final Integer version;

    public DestinationInitializer(
            final ConnectorConfiguration configuration,
            @Value("${airbyte.destination.version:1}") final Integer version) {
        this.configuration = configuration;
        this.version = version;
    }

    @Override
    public void onApplicationEvent(final StartupEvent event) {
        DestinationConfig.initialize(configuration.toJson(), version == 2);
    }
}
