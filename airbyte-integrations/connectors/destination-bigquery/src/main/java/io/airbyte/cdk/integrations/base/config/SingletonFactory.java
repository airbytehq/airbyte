package io.airbyte.cdk.integrations.base.config;

import io.airbyte.validation.json.JsonSchemaValidator;
import io.micronaut.context.annotation.Factory;
import jakarta.inject.Singleton;

/**
 * Temporary factory to enable turning classes from the CDK into singletons without
 * needing to modify the CDK.  Ultimately, all of these classes would be directly
 * annotated with the {@code @Singleton} annotation and the CDK updated to generate
 * the Micronaut singletons at compile time.
 */
@Factory
public class SingletonFactory {

    @Singleton
    public JsonSchemaValidator validator() {
        return new JsonSchemaValidator();
    }
}
