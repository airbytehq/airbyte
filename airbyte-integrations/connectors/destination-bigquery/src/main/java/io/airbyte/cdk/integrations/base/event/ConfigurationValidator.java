package io.airbyte.cdk.integrations.base.event;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.base.config.ConnectorConfiguration;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.context.event.StartupEvent;
import jakarta.inject.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.Set;

@Singleton
@Requires(bean = ConnectorConfiguration.class)
public class ConfigurationValidator implements ApplicationEventListener<StartupEvent> {

    private static final Logger LOGGER = LoggerFactory.getLogger(ConfigurationValidator.class);

    private final String connectorName;
    private final ConnectorConfiguration configuration;
    private final JsonSchemaValidator validator;

    public ConfigurationValidator(
            @Value("${micronaut.application.name}") final String connectorName,
            final ConnectorConfiguration configuration,
            final JsonSchemaValidator validator) {
        this.connectorName = connectorName;
        this.configuration = configuration;
        this.validator = validator;
    }

    @Override
    public void onApplicationEvent(final StartupEvent event) {
        try {
            final Set<String> validationResult = validator.validate(getSpecification(), configuration.toJson());
            if (!validationResult.isEmpty()) {
                throw new Exception(String.format("Verification error(s) occurred. Errors: %s ", validationResult));
            } else {
                LOGGER.info("{} connector configuration is valid.", connectorName);
            }
        } catch (final Exception e) {
            throw new RuntimeException(e);
        }
    }

    private JsonNode getSpecification() throws IOException {
        return Jsons.deserialize(MoreResources.readResource("spec.json"));
    }
}
